import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const TRIANGLE_SIDE = 70;
const TRIANGLE_HEIGHT = (Math.sqrt(3) / 2) * TRIANGLE_SIDE;
const PADDING = 10;

function isPlayableCell(value) {
  return value !== 9;
}

function isFilledValue(value) {
  return value >= 1 && value <= 6;
}

function isUpTriangle(row, col, upParity) {
  return (row + col) % 2 === upParity;
}

function getUpParityFromShape(grid) {
  for (let row = 0; row < grid.length; row += 1) {
    for (let col = 0; col < grid[row].length; col += 1) {
      if (isPlayableCell(grid[row][col])) {
        // First visible triangle is the top-left playable cell and should be "up".
        return (row + col) % 2;
      }
    }
  }

  return 0;
}

function getTriangleVertices(row, col, upParity) {
  const x = col * (TRIANGLE_SIDE / 2) + PADDING;
  const y = row * TRIANGLE_HEIGHT + PADDING;
  const up = isUpTriangle(row, col, upParity);

  if (up) {
    return [
      [x, y + TRIANGLE_HEIGHT],
      [x + TRIANGLE_SIDE, y + TRIANGLE_HEIGHT],
      [x + TRIANGLE_SIDE / 2, y],
    ];
  }

  return [
    [x, y],
    [x + TRIANGLE_SIDE, y],
    [x + TRIANGLE_SIDE / 2, y + TRIANGLE_HEIGHT],
  ];
}

function polygonPoints(vertices) {
  return vertices.map(([x, y]) => `${x},${y}`).join(" ");
}

function centroid(vertices) {
  const [a, b, c] = vertices;
  return {
    x: (a[0] + b[0] + c[0]) / 3,
    y: (a[1] + b[1] + c[1]) / 3,
  };
}

function App() {
  const [grid, setGrid] = useState([]);
  const [boardSize, setBoardSize] = useState("small"); // "small" | "big"
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [savingBoard, setSavingBoard] = useState(false);
  const [saveStatus, setSaveStatus] = useState("");

  const fetchBoard = useCallback(async () => {
    setLoading(true);
    setError("");
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/board?size=${boardSize}`);
      if (!response.ok) {
        throw new Error(`Board request failed: ${response.status}`);
      }

      const data = await response.json();
      if (!data.grid || !Array.isArray(data.grid)) {
        throw new Error("Board response does not include a valid grid.");
      }

      setGrid(data.grid);
    } catch (err) {
      setError(err.message || "Failed to load board.");
    } finally {
      setLoading(false);
    }
  }, [boardSize]);

  useEffect(() => {
    fetchBoard();
  }, [fetchBoard]);

  const handleSaveBoard = useCallback(async () => {
    setSavingBoard(true);
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/save-board`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(grid),
      });

      if (!response.ok) {
        throw new Error(`Save board failed: ${response.status}`);
      }

      const data = await response.json();
      const savePath =
        data && typeof data.path === "string"
          ? data.path
          : "Board saved successfully.";
      setSaveStatus(`Saved board to: ${savePath}`);
    } catch (err) {
      setSaveStatus(err.message || "Failed to save board.");
    } finally {
      setSavingBoard(false);
    }
  }, [grid]);

  const svgSize = useMemo(() => {
    if (grid.length === 0) {
      return { width: 400, height: 300 };
    }

    const maxCols = Math.max(...grid.map((row) => row.length));
    return {
      width: (maxCols - 1) * (TRIANGLE_SIDE / 2) + TRIANGLE_SIDE + PADDING * 2,
      height: grid.length * TRIANGLE_HEIGHT + PADDING * 2,
    };
  }, [grid]);

  const upParity = useMemo(() => getUpParityFromShape(grid), [grid]);

  const handleCellClick = useCallback(
    async (row, col, value) => {
      if (!isPlayableCell(value)) {
        return;
      }
      setSaveStatus("");

      const userInput = window.prompt(
        "Enter a value for this cell (1-6). Leave blank to cancel."
      );

      if (userInput === null || userInput.trim() === "") {
        return;
      }

      const parsedValue = Number(userInput.trim());
      if (!Number.isInteger(parsedValue) || parsedValue < 1 || parsedValue > 6) {
        window.alert("Only numbers 1 through 6 are allowed.");
        return;
      }

      try {
        const response = await fetch(
          `${API_BASE_URL}/update?row=${row}&col=${col}&value=${parsedValue}&size=${boardSize}`,
          { method: "POST" }
        );

        if (!response.ok) {
          throw new Error(`Update failed: ${response.status}`);
        }

        const data = await response.json();
        if (!data.grid || !Array.isArray(data.grid)) {
          throw new Error("Update response does not include a valid grid.");
        }

        setGrid(data.grid);
      } catch (err) {
        window.alert(err.message || "Failed to update cell.");
      }
    },
    [boardSize]
  );

  return (
    <main className="app">
      <h1>Snowflaker</h1>
      <div className="board-size-controls">
        <button
          type="button"
          onClick={() => setBoardSize("small")}
          disabled={loading || boardSize === "small"}
        >
          Small board
        </button>
        <button
          type="button"
          onClick={() => setBoardSize("big")}
          disabled={loading || boardSize === "big"}
        >
          Big board
        </button>
        <button
          type="button"
          onClick={handleSaveBoard}
          disabled={loading || savingBoard || grid.length === 0}
        >
          {savingBoard ? "Saving..." : "Save board"}
        </button>
      </div>

      {loading && <p>Loading board...</p>}
      {!loading && error && <p className="error">{error}</p>}
      {!loading && !error && saveStatus && <p>{saveStatus}</p>}

      {!loading && !error && (
        <div className="board-wrapper">
          <svg
            className="board-svg"
            viewBox={`0 0 ${svgSize.width} ${svgSize.height}`}
            aria-label="Snowflaker board"
          >
            {grid.map((row, rowIndex) =>
              row.map((cellValue, colIndex) => {
                if (!isPlayableCell(cellValue)) {
                  return null;
                }

                const vertices = getTriangleVertices(rowIndex, colIndex, upParity);
                const center = centroid(vertices);
                const displayValue = isFilledValue(cellValue) ? cellValue : "";

                return (
                  <g
                    key={`${rowIndex}-${colIndex}`}
                    className="cell-group"
                    onClick={() => handleCellClick(rowIndex, colIndex, cellValue)}
                  >
                    <polygon
                      points={polygonPoints(vertices)}
                      className="cell-triangle"
                    />
                    {displayValue !== "" && (
                      <text
                        x={center.x}
                        y={center.y}
                        className="cell-value"
                        dominantBaseline="middle"
                        textAnchor="middle"
                      >
                        {displayValue}
                      </text>
                    )}
                  </g>
                );
              })
            )}
          </svg>
        </div>
      )}
    </main>
  );
}

export default App;
