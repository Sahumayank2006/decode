from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parent / "corpus"


def ensure_dirs():
    categories = [
        "basic",
        "research_papers",
        "annual_reports",
        "government",
        "scanned",
        "unicode",
        "difficult",
        "mixed",
    ]

    for category in categories:
        (ROOT / category).mkdir(parents=True, exist_ok=True)


def save_basic():
    path = ROOT / "basic" / "basic_charts.pdf"

    with PdfPages(path) as pdf:
        # Bar
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = ["A", "B", "C", "D", "E"]
        values = [25, 42, 31, 58, 47]

        ax.bar(categories, values)
        ax.set_title("Basic Bar Chart")
        ax.set_xlabel("Category")
        ax.set_ylabel("Value")
        ax.grid(axis="y", alpha=0.25)

        pdf.savefig(fig)
        plt.close(fig)

        # Line
        fig, ax = plt.subplots(figsize=(10, 6))
        x = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        y = [10, 15, 13, 21, 26, 24]

        ax.plot(x, y, marker="o")
        ax.set_title("Basic Line Chart")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")

        pdf.savefig(fig)
        plt.close(fig)

        # Area
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(8)
        y = [5, 8, 7, 12, 15, 14, 19, 22]

        ax.fill_between(x, y, alpha=0.25)
        ax.plot(x, y)
        ax.set_title("Basic Area Chart")

        pdf.savefig(fig)
        plt.close(fig)

        # Scatter
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(20)
        y = x * 2.1 + np.random.default_rng(42).normal(0, 3, 20)

        ax.scatter(x, y)
        ax.set_title("Basic Scatter Plot")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        pdf.savefig(fig)
        plt.close(fig)


def save_pie_donut():
    path = ROOT / "basic" / "pie_donut.pdf"

    with PdfPages(path) as pdf:
        labels = ["North", "South", "East", "West"]
        values = [35, 25, 20, 20]

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title("Regional Distribution")

        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            wedgeprops={"width": 0.42},
        )
        ax.set_title("Regional Distribution - Donut")

        pdf.savefig(fig)
        plt.close(fig)


def save_tables():
    path = ROOT / "government" / "government_tables.pdf"

    with PdfPages(path) as pdf:
        fig, ax = plt.subplots(figsize=(11, 7))
        ax.axis("off")

        rows = [
            ["District", "Population", "Growth %", "Revenue"],
            ["Bhopal", "2,371,061", "8.7", "1250000"],
            ["Indore", "3,276,697", "12.4", "1875000"],
            ["Jabalpur", "1,268,848", "5.2", "932000"],
            ["Gwalior", "1,241,519", "4.8", "817000"],
            ["Ujjain", "644,758", "9.1", "534000"],
        ]

        table = ax.table(
            cellText=rows[1:],
            colLabels=rows[0],
            loc="center",
            cellLoc="center",
        )

        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)

        ax.set_title("District Statistics", pad=30)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def save_research_style():
    path = ROOT / "research_papers" / "research_style.pdf"

    with PdfPages(path) as pdf:
        fig = plt.figure(figsize=(8.5, 11))

        ax1 = fig.add_axes([0.08, 0.55, 0.38, 0.30])
        ax2 = fig.add_axes([0.54, 0.55, 0.38, 0.30])
        ax3 = fig.add_axes([0.08, 0.12, 0.38, 0.30])
        ax4 = fig.add_axes([0.54, 0.12, 0.38, 0.30])

        x = np.arange(10)

        ax1.plot(x, np.sin(x / 2))
        ax1.set_title("Experimental Results")

        ax2.bar(
            ["A", "B", "C", "D"],
            [0.71, 0.83, 0.76, 0.91],
        )
        ax2.set_title("Model Accuracy")

        ax3.scatter(
            x,
            x * 0.7 + np.random.default_rng(1).normal(0, 0.4, len(x)),
        )
        ax3.set_title("Correlation Analysis")

        ax4.plot(
            x,
            np.cumsum(np.random.default_rng(2).normal(0, 1, len(x))),
        )
        ax4.set_title("Cumulative Performance")

        fig.suptitle(
            "Research Paper — Experimental Evaluation",
            fontsize=16,
        )

        pdf.savefig(fig)
        plt.close(fig)


def save_annual_report():
    path = ROOT / "annual_reports" / "annual_report.pdf"

    with PdfPages(path) as pdf:
        fig, axes = plt.subplots(2, 2, figsize=(11, 8))

        years = ["2022", "2023", "2024", "2025"]

        axes[0, 0].bar(
            years,
            [120, 145, 178, 213],
        )
        axes[0, 0].set_title("Annual Revenue")

        axes[0, 1].plot(
            years,
            [42, 51, 63, 78],
            marker="o",
        )
        axes[0, 1].set_title("Customer Growth")

        axes[1, 0].pie(
            [40, 30, 20, 10],
            labels=["Product", "Services", "Cloud", "Other"],
        )
        axes[1, 0].set_title("Revenue Mix")

        axes[1, 1].barh(
            ["North", "South", "East", "West"],
            [91, 87, 76, 83],
        )
        axes[1, 1].set_title("Regional Performance")

        fig.suptitle(
            "Annual Business Performance Report",
            fontsize=16,
        )

        pdf.savefig(fig)
        plt.close(fig)


def save_difficult():
    path = ROOT / "difficult" / "difficult_values.pdf"

    with PdfPages(path) as pdf:
        # Large numbers
        fig, ax = plt.subplots(figsize=(12, 7))

        categories = [
            "Extremely Long Category Name A",
            "Extremely Long Category Name B",
            "Another Very Long Category Name",
            "Category With Unicode ₹",
        ]

        values = [
            1_000_000_000,
            0.000001,
            -500,
            250_000_000,
        ]

        ax.bar(categories, values)
        ax.set_title("Extreme Numeric Range")
        ax.tick_params(axis="x", rotation=25)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # Sparse / zero values
        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(10)
        y = [0, 10, np.nan, 30, 0, 50, np.nan, 20, 0, 40]

        ax.plot(x, y, marker="o")
        ax.set_title("Sparse and Missing Values")

        pdf.savefig(fig)
        plt.close(fig)


def save_unicode():
    path = ROOT / "unicode" / "unicode_charts.pdf"

    with PdfPages(path) as pdf:
        fig, ax = plt.subplots(figsize=(11, 7))

        labels = [
            "भारत",
            "मध्य प्रदेश",
            "राजस्व ₹",
            "वृद्धि %",
            "Café",
            "São Paulo",
        ]

        values = [25, 42, 37, 55, 31, 48]

        ax.bar(labels, values)
        ax.set_title("बहुभाषी डेटा — Multilingual Data")
        ax.set_xlabel("श्रेणी / Category")
        ax.set_ylabel("मूल्य / Value")
        ax.tick_params(axis="x", rotation=25)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def save_mixed():
    path = ROOT / "mixed" / "mixed_document.pdf"

    with PdfPages(path) as pdf:
        fig = plt.figure(figsize=(11, 8))

        ax1 = fig.add_axes([0.08, 0.55, 0.40, 0.32])
        ax2 = fig.add_axes([0.55, 0.55, 0.37, 0.32])
        ax3 = fig.add_axes([0.08, 0.10, 0.40, 0.32])
        ax4 = fig.add_axes([0.55, 0.10, 0.37, 0.32])

        ax1.bar(["A", "B", "C"], [20, 40, 30])
        ax1.set_title("Bar")

        ax2.plot(["Q1", "Q2", "Q3", "Q4"], [10, 25, 18, 35])
        ax2.set_title("Line")

        ax3.pie([40, 35, 25], labels=["A", "B", "C"])
        ax3.set_title("Pie")

        ax4.scatter(
            [1, 2, 3, 4, 5],
            [3, 5, 4, 8, 7],
        )
        ax4.set_title("Scatter")

        fig.suptitle("Mixed Visualization Document")

        pdf.savefig(fig)
        plt.close(fig)


def main():
    ensure_dirs()

    save_basic()
    save_pie_donut()
    save_tables()
    save_research_style()
    save_annual_report()
    save_difficult()
    save_unicode()
    save_mixed()

    print()
    print("=" * 60)
    print("DECODE SYNTHETIC PDF CORPUS GENERATED")
    print("=" * 60)

    for pdf in sorted(ROOT.rglob("*.pdf")):
        print(pdf.relative_to(ROOT))

    print("=" * 60)


if __name__ == "__main__":
    main()
