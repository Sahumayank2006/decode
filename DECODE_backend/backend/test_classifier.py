import cv2
import numpy as np
from core.chart_detector import detect_charts_in_image

def test_bar_chart_no_axis():
    print("\n--- Test 1: Bar Chart (NO AXIS) ---")
    # Draw 3 vertical bars on a baseline, no text
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (100, 400), (150, 100), (200, 0, 0), -1)
    cv2.rectangle(img, (200, 400), (250, 200), (200, 0, 0), -1)
    cv2.rectangle(img, (300, 400), (350, 150), (200, 0, 0), -1)
    # Baseline
    cv2.line(img, (50, 400), (450, 400), (0, 0, 0), 2)
    
    res = detect_charts_in_image(img)
    for r in res:
        sub = f" ({r['sub_type']})" if r.get('sub_type') else ""
        print(f"Result: {r['chart_type']}{sub} ({r['confidence']:.2f}) - {r['reason']}")
        print(f"Negative Evidence: {r['negative_evidence']}")

def test_bar_chart_with_axis():
    print("\n--- Test 2: Bar Chart (WITH NUMERIC AXIS) ---")
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    # Bars
    cv2.rectangle(img, (150, 400), (200, 100), (200, 0, 0), -1)
    cv2.rectangle(img, (250, 400), (300, 200), (200, 0, 0), -1)
    cv2.rectangle(img, (350, 400), (400, 150), (200, 0, 0), -1)
    # Axes
    cv2.line(img, (100, 50), (100, 400), (0, 0, 0), 2)
    cv2.line(img, (100, 400), (450, 400), (0, 0, 0), 2)
    # Numeric Labels
    cv2.putText(img, "100", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "50", (30, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "0", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    
    res = detect_charts_in_image(img)
    for r in res:
        sub = f" ({r['sub_type']})" if r.get('sub_type') else ""
        print(f"Result: {r['chart_type']}{sub} ({r['confidence']:.2f}) - {r['reason']}")
        print(f"Evidence: {r['evidence']}")

def test_diagram_with_text():
    print("\n--- Test 3: Diagram with Text Nodes (NO AXIS) ---")
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    # Nodes
    cv2.rectangle(img, (50, 100), (200, 200), (0, 0, 0), 2)
    cv2.rectangle(img, (300, 100), (450, 200), (0, 0, 0), 2)
    cv2.rectangle(img, (150, 300), (350, 400), (0, 0, 0), 2)
    # Text inside nodes
    cv2.putText(img, "Server", (70, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "Database", (310, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.putText(img, "Client Node", (170, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    # Connectors
    cv2.line(img, (200, 150), (300, 150), (0, 0, 0), 2)
    cv2.line(img, (125, 200), (200, 300), (0, 0, 0), 2)
    
    res = detect_charts_in_image(img)
    for r in res:
        print(f"Result: {r['chart_type']} ({r['confidence']}) - {r['reason']}")
        print(f"Evidence: {r['evidence']}")

if __name__ == "__main__":
    test_bar_chart_no_axis()
    test_bar_chart_with_axis()
    test_diagram_with_text()
