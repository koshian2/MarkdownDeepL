document.addEventListener("DOMContentLoaded", (event) => {
    eel.load_settings();
})

document.getElementById("translate").onclick = async () => {
    const sourceText = document.getElementById("source_text").value;
    const translatedResult = await eel.translate(sourceText)();
    document.getElementById("target_text").value = translatedResult[0];
    document.getElementById("footer").innerText = translatedResult[1];
}

eel.expose(updateMasterData)
function updateMasterData(masterData) {
    document.getElementById("source_lang").value = masterData["source_lang"];
    document.getElementById("target_lang").value = masterData["target_lang"];
}