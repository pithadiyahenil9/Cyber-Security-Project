const API = "http://127.0.0.1:8000";

// Generate Hash
async function generateHash() {
    const text = document.getElementById("hashText").value;
    const algorithm = document.getElementById("hashAlgo").value;

    const res = await fetch(`${API}/hash`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, algorithm })
    });

    const data = await res.json();
    document.getElementById("hashOutput").innerText = data.hash;
}


// Crack Hash
async function crackHash() {
    const hash_value = document.getElementById("crackHashInput").value;
    const algorithm = document.getElementById("crackAlgo").value;

    // 1) Save wordlist in backend storage
    await storeWordlist();

    // 2) Trigger crack job
    const res = await fetch(`${API}/crack`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            hash_value,
            algorithm,
            wordlist: [] // no longer needed
        })
    });

    const data = await res.json();

    if (data.found) {
        document.getElementById("crackOutput").innerText =
            `Password Found: ${data.password}`;
    } else {
        document.getElementById("crackOutput").innerText =
            `Password Not Found`;
    }
}

// Wordlist Generator
async function generateWordlist() {
    const charset = document.getElementById("charsetOption").value;
    const min_len = parseInt(document.getElementById("minLength").value);
    const max_len = parseInt(document.getElementById("maxLength").value);

    const res = await fetch(`${API}/wordlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ charset, min_len, max_len })
    });

    const data = await res.json();
    document.getElementById("wordlistOutput").innerText =
        data.preview.join(", ");
}


// Mutations
async function applyMutations() {
    const words = document.getElementById("mutationWords").value.split(",");

    const res = await fetch(`${API}/mutate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ words })
    });

    const data = await res.json();
    document.getElementById("mutationOutput").innerText =
        data.mutations.join(", ");
}




async function storeWordlist() {
    let raw = document.getElementById("crackWordlist").value;

    let words = raw
        .split(",")
        .map(w => w.trim())
        .filter(w => w.length > 0);

    const res = await fetch(`${API}/store_wordlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            hash_value: "",
            algorithm: "",
            wordlist: words
        })
    });

    return await res.json();
}



async function compareSpeed() {
    const algorithm = document.getElementById("compareAlgo").value;

    const res = await fetch(`${API}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "", algorithm })
    });

    const data = await res.json();

    document.getElementById("speedOutput").innerText =
        `Python Speed: ${data.python_speed}
Hashcat GPU Speed: ${data.hashcat_speed}
Difference: ${data.difference}`;
}