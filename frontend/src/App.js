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
  const [clearingBoard, setClearingBoard] = useState(false);
  const [solvingBoard, setSolvingBoard] = useState(false);
  const [saveStatus, setSaveStatus] = useState("");
  const [puzzleSet, setPuzzleSet] = useState(false);
  const [mistakes, setMistakes] = useState([]);
  const [settingPuzzle, setSettingPuzzle] = useState(false);
  const [checkingMistakes, setCheckingMistakes] = useState(false);
  const [selectedCell, setSelectedCell] = useState(null); // { row, col } or null

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
      setMistakes([]);
    } catch (err) {
      setError(err.message || "Failed to load board.");
    } finally {
      setLoading(false);
    }
  }, [boardSize]);

  const fetchPuzzleStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/puzzle?size=${boardSize}`);
      if (!response.ok) return;
      const data = await response.json();
      setPuzzleSet(data.set === true);
    } catch {
      setPuzzleSet(false);
    }
  }, [boardSize]);

  useEffect(() => {
    if (!loading && !error) fetchPuzzleStatus();
  }, [loading, error, fetchPuzzleStatus]);

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

  const handleSolveBoard = useCallback(async () => {
    setSolvingBoard(true);
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/solve-board?size=${boardSize}`, {
        method: "POST",
      });

      const data = await response.json();
      if (!response.ok) {
        const detail =
          data && typeof data.detail === "string"
            ? data.detail
            : `Solve board failed: ${response.status}`;
        throw new Error(detail);
      }

      if (!data.grid || !Array.isArray(data.grid)) {
        throw new Error("Solve response does not include a valid grid.");
      }

      setGrid(data.grid);
      setMistakes([]);
      setSaveStatus("Board solved.");
    } catch (err) {
      setSaveStatus(err.message || "Failed to solve board.");
    } finally {
      setSolvingBoard(false);
    }
  }, [boardSize]);

  const handleClearBoard = useCallback(async () => {
    setClearingBoard(true);
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/clear-board?size=${boardSize}`, {
        method: "POST",
      });

      const data = await response.json();
      if (!response.ok) {
        const detail =
          data && typeof data.detail === "string"
            ? data.detail
            : `Clear board failed: ${response.status}`;
        throw new Error(detail);
      }

      if (!data.grid || !Array.isArray(data.grid)) {
        throw new Error("Clear response does not include a valid grid.");
      }

      setGrid(data.grid);
      setMistakes([]);
      setSaveStatus("Board cleared.");
      fetchPuzzleStatus();
    } catch (err) {
      setSaveStatus(err.message || "Failed to clear board.");
    } finally {
      setClearingBoard(false);
    }
  }, [boardSize, fetchPuzzleStatus]);

  const handleSetPuzzle = useCallback(async () => {
    setSettingPuzzle(true);
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/set-puzzle?size=${boardSize}`, {
        method: "POST",
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Set puzzle failed: ${response.status}`);
      }
      setMistakes([]);
      setPuzzleSet(true);
      setSaveStatus("Current board set as puzzle. Fill in your answers and use Find mistakes.");
    } catch (err) {
      setSaveStatus(err.message || "Failed to set puzzle.");
    } finally {
      setSettingPuzzle(false);
    }
  }, [boardSize]);

  const handleCheckMistakes = useCallback(async () => {
    setCheckingMistakes(true);
    setSaveStatus("");

    try {
      const response = await fetch(`${API_BASE_URL}/check-mistakes?size=${boardSize}`, {
        method: "POST",
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Check mistakes failed: ${response.status}`);
      }

      const list = data.mistakes || [];
      setMistakes(list);
      if (list.length === 0) {
        setSaveStatus("No mistakes — all filled cells are correct!");
      } else {
        setSaveStatus(`${list.length} mistake(s) found. Incorrect cells are highlighted.`);
      }
    } catch (err) {
      setSaveStatus(err.message || "Failed to check mistakes.");
    } finally {
      setCheckingMistakes(false);
    }
  }, [boardSize]);

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

  const applyValueToCell = useCallback(
    async (row, col, value) => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/update?row=${row}&col=${col}&value=${value}&size=${boardSize}`,
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
        setMistakes((prev) => prev.filter((m) => m.row !== row || m.col !== col));
      } catch (err) {
        window.alert(err.message || "Failed to update cell.");
      }
    },
    [boardSize]
  );

  const handleCellClick = useCallback((row, col, value) => {
    if (!isPlayableCell(value)) {
      return;
    }
    setSaveStatus("");
    setSelectedCell({ row, col });
  }, []);

  useEffect(() => {
    if (!selectedCell) return;

    const onKeyDown = (e) => {
      if (e.key === "Escape") {
        setSelectedCell(null);
        return;
      }
      const num = parseInt(e.key, 10);
      if (num >= 1 && num <= 6) {
        e.preventDefault();
        applyValueToCell(selectedCell.row, selectedCell.col, num);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [selectedCell, applyValueToCell]);

  const isMistakeCell = useCallback(
    (row, col) => mistakes.some((m) => m.row === row && m.col === col),
    [mistakes]
  );
  const getMistakeInfo = useCallback(
    (row, col) => mistakes.find((m) => m.row === row && m.col === col),
    [mistakes]
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
          disabled={
            loading || savingBoard || solvingBoard || clearingBoard || grid.length === 0
          }
        >
          {savingBoard ? "Saving..." : "Save board"}
        </button>
        <button
          type="button"
          onClick={handleClearBoard}
          disabled={loading || clearingBoard || savingBoard || solvingBoard || grid.length === 0}
        >
          {clearingBoard ? "Clearing..." : "Clear board"}
        </button>
        <button
          type="button"
          onClick={handleSolveBoard}
          disabled={loading || solvingBoard || savingBoard || clearingBoard || grid.length === 0}
        >
          {solvingBoard ? "Solving..." : "Solve board"}
        </button>
        <button
          type="button"
          onClick={handleSetPuzzle}
          disabled={
            loading || settingPuzzle || solvingBoard || clearingBoard || savingBoard || grid.length === 0
          }
        >
          {settingPuzzle ? "Setting..." : "Set as puzzle"}
        </button>
        <button
          type="button"
          onClick={handleCheckMistakes}
          disabled={
            loading || checkingMistakes || !puzzleSet || solvingBoard || clearingBoard || grid.length === 0
          }
          title={!puzzleSet ? "Set a puzzle first" : "Compare your answers with the solution"}
        >
          {checkingMistakes ? "Checking..." : "Find mistakes"}
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
                const mistake = isMistakeCell(rowIndex, colIndex);
                const mistakeInfo = getMistakeInfo(rowIndex, colIndex);
                const selected =
                  selectedCell &&
                  selectedCell.row === rowIndex &&
                  selectedCell.col === colIndex;

                return (
                  <g
                    key={`${rowIndex}-${colIndex}`}
                    className="cell-group"
                    onClick={() => handleCellClick(rowIndex, colIndex, cellValue)}
                  >
                    <polygon
                      points={polygonPoints(vertices)}
                      className={`cell-triangle${mistake ? " cell-mistake" : ""}${selected ? " cell-selected" : ""}`}
                    />
                    {displayValue !== "" && (
                      <text
                        x={center.x}
                        y={center.y}
                        className={`cell-value${mistake ? " cell-value-mistake" : ""}`}
                        dominantBaseline="middle"
                        textAnchor="middle"
                      >
                        {displayValue}
                      </text>
                    )}
                    {mistake && mistakeInfo && (
                      <title>
                        Your answer: {mistakeInfo.userValue}. Correct: {mistakeInfo.correctValue}
                      </title>
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
