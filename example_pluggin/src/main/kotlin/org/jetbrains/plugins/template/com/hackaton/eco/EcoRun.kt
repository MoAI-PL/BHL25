package com.hackathon.eco

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.command.WriteCommandAction // Ważne: Pozwala edytować kod
import com.intellij.openapi.ui.Messages

class EcoRun : AnAction() {

    override fun actionPerformed(e: AnActionEvent) {
        // 1. Pobieramy potrzebne elementy: Projekt, Edytor i Dokument (plik)
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val document = editor.document
        
        // 2. Pobieramy zaznaczony tekst
        val selectionModel = editor.selectionModel
        val selectedText = selectionModel.selectedText

        if (selectedText.isNullOrEmpty()) {
            return
        }

        // 3. LOGIKA: Przerabiamy tekst linijka po linijce
        // lines() dzieli tekst na listę. joinToString() skleja go z powrotem.
        val nowyTekstZKotami = selectedText.lines().joinToString("\n") { linijka ->
            if (linijka.contains("for")) {
                // Jeśli jest pętla, doklejamy kota na końcu
                "$linijka  # 🐱 TU JEST PĘTLA!" 
            } else {
                // Jeśli nie ma, zostawiamy bez zmian
                linijka
            }
        }

        // 4. EDYCJA: Bezpieczne wprowadzanie zmian (Write Action)
        // To jest jak "Tryb Administratora" dla edycji kodu
        WriteCommandAction.runWriteCommandAction(project) {
            document.replaceString(
                selectionModel.selectionStart, 
                selectionModel.selectionEnd, 
                nowyTekstZKotami
            )
        }
        
        // 5. Opcjonalnie: Daj znać, że gotowe (żebyś wiedział, że zadziałało)
        // Możesz to usunąć, jeśli wolisz ciszę.
       /* Messages.showInfoMessage(
            "Oznaczyłem wszystkie pętle kotami! 🐱", 
            "Koci Inspektor"
        ) */
    }
}