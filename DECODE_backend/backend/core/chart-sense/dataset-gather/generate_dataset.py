#!/usr/bin/env python3
"""
Dataset Generator for Chart Sense

Generates training data by:
1. Loading chart page with different seed values
2. Capturing screenshots of rendered charts
3. Extracting ECharts JSON configuration
4. Saving paired image + JSON files
"""

import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Error as PlaywrightError

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@dataclass
class Config:
    """Configuration for dataset generation."""
    dataset_dir: Path = Path("dataset")
    chart_url: str = "http://localhost:5173"
    num_samples: int = 100
    image_width: int = 600
    image_height: int = 400
    browser: str = "firefox"
    headless: bool = True
    timeout: int = 5000
    render_delay: int = 200
    # Chart generation parameters
    chart_type: str = "bar"  # bar, line, area, pie, doughnut OR template ID
    # Use specific template (overrides chart_type)
    template_id: Optional[str] = None
    data_size: int = 5
    min_value: float = 0.0
    max_value: float = 100.0
    color_scheme: str = "vibrant"  # vibrant, pastel, monochrome, earth, ocean
    include_negatives: bool = False
    seed_offset: int = 0  # Base seed offset for generating different datasets


class Logger:
    """Simple colored logger for CLI output."""

    @staticmethod
    def info(msg: str) -> None:
        print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

    @staticmethod
    def success(msg: str) -> None:
        print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

    @staticmethod
    def warning(msg: str) -> None:
        print(f"{Fore.YELLOW}⚠ {msg}{Style.RESET_ALL}")

    @staticmethod
    def error(msg: str) -> None:
        print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}", file=sys.stderr)

    @staticmethod
    def header(msg: str) -> None:
        print(f"\n{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{msg}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}\n")


def ensure_dataset_dir(config: Config) -> None:
    """Create dataset directory if it doesn't exist."""
    try:
        config.dataset_dir.mkdir(exist_ok=True)
        Logger.info(f"Dataset directory: {config.dataset_dir.absolute()}")
    except Exception as e:
        Logger.error(f"Failed to create dataset directory: {e}")
        raise


def capture_chart(
    page: Page,
    seed: int,
    config: Config
) -> tuple[Optional[dict], Optional[str]]:
    """
    Capture a single chart screenshot and configuration.

    Returns:
        Tuple of (chart_config, error_message)
        chart_config is None if error occurred
    """
    try:
        # Build URL with chart generation parameters
        url_params = {
            'seed': seed,
            'type': config.chart_type,
            'dataSize': config.data_size,
            'minValue': config.min_value,
            'maxValue': config.max_value,
            'colorScheme': config.color_scheme,
            'includeNegatives': str(config.include_negatives).lower()
        }

        # Add template ID if specified
        if config.template_id:
            url_params['templateId'] = config.template_id

        query_string = "&".join(f"{k}={v}" for k, v in url_params.items())
        url = f"{config.chart_url}?{query_string}"

        page.goto(url, wait_until="networkidle", timeout=config.timeout)

        # Wait for chart to be ready
        page.wait_for_function(
            "window.chartReady === true",
            timeout=config.timeout
        )

        # Give ECharts time to finish rendering animations
        page.wait_for_timeout(config.render_delay)

        # Extract chart configuration from page
        chart_config = page.evaluate("() => window.chartConfig")

        if not chart_config:
            return None, "Chart configuration is empty or null"

        # Generate filenames
        filename = f"{seed:06d}"
        image_path = config.dataset_dir / f"{filename}.png"
        json_path = config.dataset_dir / f"{filename}.json"

        # Screenshot the chart element
        chart_element = page.locator("#chart")
        if not chart_element.count():
            return None, "Chart element '#chart' not found on page"

        chart_element.screenshot(path=str(image_path))

        # Save JSON configuration
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(chart_config, f, indent=2, ensure_ascii=False)

        return chart_config, None

    except PlaywrightError as e:
        return None, f"Playwright error: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"JSON encoding error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def generate_dataset(config: Config) -> None:
    """Generate dataset of chart images and configurations."""
    ensure_dataset_dir(config)

    Logger.header("Dataset Generation Starting")
    Logger.info(f"Target samples: {config.num_samples}")
    Logger.info(f"Chart URL: {config.chart_url}")
    Logger.info(
        f"Browser: {config.browser} ({'headless' if config.headless else 'headful'})")

    # Chart configuration details
    if config.template_id:
        Logger.info(f"Template: {config.template_id}")
    else:
        Logger.info(f"Chart type: {config.chart_type}")
        Logger.info(
            f"Data size: {config.data_size}, Value range: [{config.min_value}, {config.max_value}]")
        Logger.info(
            f"Color scheme: {config.color_scheme}, Negatives: {config.include_negatives}")

    Logger.info(f"Output: {config.dataset_dir.absolute()}")
    print()

    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None

    try:
        with sync_playwright() as p:
            # Launch browser
            browser_type = getattr(p, config.browser, None)
            if not browser_type:
                Logger.error(f"Browser '{config.browser}' not supported")
                return

            browser = browser_type.launch(headless=config.headless)
            context = browser.new_context(
                viewport={"width": config.image_width,
                          "height": config.image_height}
            )
            page = context.new_page()

            success_count = 0
            error_count = 0
            errors_detail = []

            for i in range(config.num_samples):
                # Real-time progress for smaller batches
                if config.num_samples <= 20:
                    Logger.info(
                        f"Generating sample {i+1}/{config.num_samples}...")

                chart_config, error = capture_chart(
                    page, i + config.seed_offset, config)

                if error:
                    error_count += 1
                    errors_detail.append((i, error))
                    Logger.error(f"Sample {i:06d} failed: {error}")
                else:
                    success_count += 1
                    if config.num_samples <= 20:
                        Logger.success(
                            f"Sample {i:06d} generated successfully")

                    # Progress indicator for larger batches
                    if config.num_samples > 20 and (i + 1) % 10 == 0:
                        Logger.success(
                            f"Progress: {i + 1}/{config.num_samples} "
                            f"({success_count} success, {error_count} errors)"
                        )

            # Summary
            Logger.header("Generation Complete")
            Logger.success(f"Successful: {success_count}/{config.num_samples}")

            if error_count > 0:
                Logger.warning(f"Failed: {error_count}/{config.num_samples}")

                # Show first 5 errors in detail
                if errors_detail:
                    print(
                        f"\n{Fore.YELLOW}First errors encountered:{Style.RESET_ALL}")
                    for seed, err in errors_detail[:5]:
                        print(
                            f"  {Fore.RED}Sample {seed:06d}:{Style.RESET_ALL} {err}")

                    if len(errors_detail) > 5:
                        print(f"  ... and {len(errors_detail) - 5} more")

            Logger.info(f"Dataset location: {config.dataset_dir.absolute()}")

    except KeyboardInterrupt:
        Logger.warning("\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Fatal error during generation: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Ensure proper cleanup with error handling
        cleanup_errors = []

        if context:
            try:
                context.close()
            except Exception as e:
                cleanup_errors.append(f"Context cleanup: {e}")

        if browser:
            try:
                browser.close()
            except Exception as e:
                cleanup_errors.append(f"Browser cleanup: {e}")

        # Only log cleanup errors if they're not the common event loop issue
        for error in cleanup_errors:
            if "Event loop is closed" not in error:
                Logger.warning(f"Cleanup warning: {error}")


def verify_dataset(config: Config) -> None:
    """Verify dataset integrity and show statistics."""
    if not config.dataset_dir.exists():
        Logger.error("Dataset directory not found")
        return

    png_files = list(config.dataset_dir.glob("*.png"))
    json_files = list(config.dataset_dir.glob("*.json"))

    Logger.header("Dataset Verification")
    Logger.info(f"Images: {len(png_files)}")
    Logger.info(f"JSON files: {len(json_files)}")

    # Check for orphaned files
    png_stems = {f.stem for f in png_files}
    json_stems = {f.stem for f in json_files}

    orphaned_pngs = png_stems - json_stems
    orphaned_jsons = json_stems - png_stems

    if orphaned_pngs:
        Logger.warning(f"Orphaned images (no JSON): {len(orphaned_pngs)}")
        if len(orphaned_pngs) <= 10:
            for stem in sorted(orphaned_pngs):
                print(f"  - {stem}.png")

    if orphaned_jsons:
        Logger.warning(
            f"Orphaned JSON files (no image): {len(orphaned_jsons)}")
        if len(orphaned_jsons) <= 10:
            for stem in sorted(orphaned_jsons):
                print(f"  - {stem}.json")

    if not orphaned_pngs and not orphaned_jsons and len(png_files) > 0:
        Logger.success("All files properly paired")
    elif len(png_files) == 0:
        Logger.warning("Dataset is empty")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate chart dataset for Chart Sense ML training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -n 1000                    Generate 1000 samples with Firefox
  %(prog)s -b chromium -n 500         Generate 500 samples with Chromium
  %(prog)s --verify                   Verify existing dataset integrity
  %(prog)s -n 100 --headful           Generate with visible browser window
        """
    )

    parser.add_argument(
        "-n", "--num-samples",
        type=int,
        default=100,
        metavar="N",
        help="Number of samples to generate (default: 100)"
    )

    parser.add_argument(
        "-b", "--browser",
        type=str,
        default="firefox",
        choices=["firefox", "chromium", "webkit"],
        help="Browser to use (default: firefox)"
    )

    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser in headful mode (visible window, useful for debugging)"
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing dataset instead of generating new data"
    )

    parser.add_argument(
        "--chart-type",
        type=str,
        default="bar",
        choices=["bar", "line", "area", "pie", "doughnut"],
        help="Type of chart to generate (default: bar)"
    )

    parser.add_argument(
        "--template",
        type=str,
        metavar="TEMPLATE_ID",
        help="Use specific chart template (overrides --chart-type). Available: basic-bar, multi-series-bar, advanced-pie, trend-lines, edge-cases"
    )

    parser.add_argument(
        "--data-size",
        type=int,
        default=5,
        metavar="N",
        help="Number of data points per chart (default: 5)"
    )

    parser.add_argument(
        "--min-value",
        type=float,
        default=0.0,
        metavar="MIN",
        help="Minimum data value (default: 0.0)"
    )

    parser.add_argument(
        "--max-value",
        type=float,
        default=100.0,
        metavar="MAX",
        help="Maximum data value (default: 100.0)"
    )

    parser.add_argument(
        "--color-scheme",
        type=str,
        default="vibrant",
        choices=["vibrant", "pastel", "monochrome", "earth", "ocean"],
        help="Color scheme for charts (default: vibrant)"
    )

    parser.add_argument(
        "--include-negatives",
        action="store_true",
        help="Allow negative values in data"
    )

    parser.add_argument(
        "--seed-offset",
        type=int,
        default=0,
        metavar="OFFSET",
        help="Base seed offset for generating different datasets (default: 0)"
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:5173",
        metavar="URL",
        help="Chart generator URL (default: http://localhost:5173)"
    )

    args = parser.parse_args()

    # Build configuration
    config = Config(
        num_samples=args.num_samples,
        browser=args.browser,
        headless=not args.headful,
        chart_url=args.url,
        chart_type=args.chart_type,
        template_id=args.template,
        data_size=args.data_size,
        min_value=args.min_value,
        max_value=args.max_value,
        color_scheme=args.color_scheme,
        include_negatives=args.include_negatives,
        seed_offset=args.seed_offset,
    )

    if args.verify:
        verify_dataset(config)
    else:
        generate_dataset(config)
        print()  # Empty line before verification
        verify_dataset(config)
