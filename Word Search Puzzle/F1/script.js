let wordsToFind = [];
let selectedCells = [];
let startTime;

document.getElementById("uploadButton").addEventListener("click", async () => {
    const pdfInput = document.getElementById("pdfInput").files[0];
    const statusMessage = document.getElementById("statusMessage");

    if (!pdfInput) {
        statusMessage.textContent = "Please select a PDF!";
        return;
    }

    statusMessage.textContent = "Processing the PDF... Please wait.";

    const formData = new FormData();
    formData.append("pdf", pdfInput);

    try {
        const response = await fetch("http://127.0.0.1:5000/", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        if (response.ok) {
            wordsToFind = data.words;
            statusMessage.textContent = "Select The Following Words In The Grid: " + wordsToFind.join(", ");
            startGame();
        } else {
            statusMessage.textContent = "Error: " + data.error;
        }
    } catch (error) {
        statusMessage.textContent = "An error occurred during upload.";
        console.error("Error during PDF upload:", error);
    }
});

function startGame() {
    startTime = Date.now();
    generatePuzzle(wordsToFind);
    document.getElementById("verifyWordButton").style.display = "block";
}

function generatePuzzle(words) {
    const gridSize = 10;
    const grid = Array.from({ length: gridSize }, () => Array(gridSize).fill(""));

    words.forEach(word => placeWordInGrid(word, grid));

    // Fill empty cells with random letters
    for (let row = 0; row < gridSize; row++) {
        for (let col = 0; col < gridSize; col++) {
            if (!grid[row][col]) {
                grid[row][col] = String.fromCharCode(65 + Math.floor(Math.random() * 26));
            }
        }
    }
    displayPuzzle(grid);
}

function placeWordInGrid(word, grid) {
    const gridSize = grid.length;
    let placed = false;
    let attempts = 0;
    const maxAttempts = 100;

    while (!placed && attempts < maxAttempts) {
        const direction = Math.random() < 0.5 ? "horizontal" : "vertical";
        const row = Math.floor(Math.random() * gridSize);
        const col = Math.floor(Math.random() * gridSize);

        if (direction === "horizontal" && col + word.length <= gridSize) {
            if (word.split("").every((_, i) => !grid[row][col + i])) {
                word.split("").forEach((char, i) => (grid[row][col + i] = char));
                placed = true;
            }
        } else if (direction === "vertical" && row + word.length <= gridSize) {
            if (word.split("").every((_, i) => !grid[row + i][col])) {
                word.split("").forEach((char, i) => (grid[row + i][col] = char));
                placed = true;
            }
        }
        attempts++;
    }

    if (!placed) console.warn(`Failed to place word: ${word}`);
}

function displayPuzzle(grid) {
    const puzzleContainer = document.getElementById("puzzleContainer");
    puzzleContainer.innerHTML = "";
    const fragment = document.createDocumentFragment();

    grid.forEach((row, rowIndex) => {
        row.forEach((letter, colIndex) => {
            const cell = document.createElement("div");
            cell.textContent = letter;
            cell.dataset.row = rowIndex;
            cell.dataset.col = colIndex;
            cell.id = `cell-${rowIndex}-${colIndex}`;
            cell.classList.add("puzzle-cell");
            cell.addEventListener("click", () => selectCell(cell));
            fragment.appendChild(cell);
        });
    });

    puzzleContainer.appendChild(fragment);
}

function selectCell(cell) {
    if (cell.classList.contains("selected")) {
        cell.classList.remove("selected");
        selectedCells = selectedCells.filter(
            c => c.row !== cell.dataset.row || c.col !== cell.dataset.col
        );
    } else {
        cell.classList.add("selected");
        selectedCells.push({
            row: parseInt(cell.dataset.row, 10),
            col: parseInt(cell.dataset.col, 10),
            letter: cell.textContent
        });
    }
}

document.getElementById("verifyWordButton").addEventListener("click", async () => {
    if (selectedCells.length === 0) {
        alert("Please select letters to form a word!");
        return;
    }

    const selectedWord = selectedCells.map(cell => cell.letter).join("");

    try {
        const response = await fetch("http://127.0.0.1:5000/validate_word", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ word: selectedWord }),
        });

        const data = await response.json();

        if (data.valid) {
            alert(`Correct! You found: ${selectedWord}`);
            selectedCells.forEach(cell => {
                const gridCell = document.getElementById(`cell-${cell.row}-${cell.col}`);
                gridCell.classList.add("correct");
                gridCell.classList.remove("selected");
            });
            wordsToFind = wordsToFind.filter(word => word !== selectedWord);
        } else {
            alert("Wrong word. Try again.");
            selectedCells.forEach(cell => {
                const gridCell = document.getElementById(`cell-${cell.row}-${cell.col}`);
                gridCell.classList.remove("selected");
            });
        }

        selectedCells = [];
        if (wordsToFind.length === 0) displayScore();

    } catch (error) {
        alert("An error occurred while validating the word.");
        console.error("Error during word validation:", error);
    }
});

async function displayScore() {
    try {
        const response = await fetch("http://127.0.0.1:5000/score", { method: "POST" });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        const timeTaken = Math.floor((Date.now() - startTime) / 1000);

        document.getElementById("scoreDisplay").textContent = `Score: ${data.score} points. Time: ${timeTaken}s. Mistakes: ${data.fail_attempts}`;
        document.getElementById("scoreSection").style.display = "block";
        document.getElementById("verifyWordButton").style.display = "none";
    } catch (error) {
        console.error("Error fetching score:", error);
        document.getElementById("scoreDisplay").textContent = "Failed to fetch score.";
    }
}
