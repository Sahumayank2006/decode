from core.demo.service import DemoService


def main():
    print("=" * 60)
    print("DECODE DEMO API TEST")
    print("=" * 60)

    service = DemoService()

    # --------------------------------------------------------------
    # Health
    # --------------------------------------------------------------

    health = service.health()

    assert health["success"] is True
    assert health["data"]["service"] == "DECODE"
    assert health["data"]["status"] == "healthy"

    print("HEALTH TEST PASSED")

    # --------------------------------------------------------------
    # Capabilities
    # --------------------------------------------------------------

    capabilities = service.capabilities()

    assert capabilities["success"] is True

    supported_types = {
        item["chart_type"]
        for item in capabilities["data"]["chart_types"]
        if item["supported"]
    }

    expected = {
        "bar",
        "line",
        "area",
        "scatter",
        "pie",
        "donut",
        "table",
    }

    assert expected.issubset(supported_types), (
        f"Missing visualization types: "
        f"{expected - supported_types}"
    )

    print("CAPABILITIES TEST PASSED")

    # --------------------------------------------------------------
    # Product information
    # --------------------------------------------------------------

    product = service.product_info()

    assert product["success"] is True
    assert product["data"]["name"] == "DECODE"

    print("PRODUCT INFO TEST PASSED")

    print("=" * 60)
    print("DECODE DEMO API TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
