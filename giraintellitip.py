import sublime_plugin, sublime, json, webbrowser
import re, os
from time import time

settings = {}

class GiraintellitipCommand(sublime_plugin.TextCommand):
    css = """<style>
body {
    font-size: 12px;
    font-family: sans-serif;
}

h1 {
    font-size: 14px;
}
</style>"""

    codes = {
    "5000": "Definition für HS/FS-Experte",
    "4999": "Definition mehrerer Sprachen",
    "5001": "Definition des Bausteins",
    "5002": "Definition des Eingangs",
    "5003": "Definition einer Speichervariable",
    "5004": "Definition eines Ausgangs",
    "5012": "Definition einer Formelzeile"
    }

    def loadDB(self):
        path_db = os.path.dirname(os.path.abspath(__file__))+"/docs.json"
        if os.path.exists(path_db):
            self.cache = json.load(open(path_db))

    def getHelpTitle(self, code):
        return self.codes[code]

    def getHelpText(self, code, params, paramIdx):
        txt = ""
        if (code == 5000):
            paramDef = ["Satzart", "Bezeichnung", "Remanent", "Anzahl Eingänge", "Bezeichnung Eingang n", "Anzahl Ausgänge", "Bezeichnung Ausgang n", "Versions-Nr."]
            paramType = ["Zahl", "Text", "Zahl", "Zahl", "Text", "Zahl", "Text", "Text"]
            paramDesc = ["Satzart", "Es darf eine beliebige Kategorietiefe verwendet werden! (Bsp: Kat1\Kat2\Kat3\Kat4\Baustein wäre gültig) Beispiel ohne Kategorie: UND-Gatter (2 Eingänge) Beispiel mit einer Kategorie: Weitere Bausteine\Telegrammgenerator", "Ist dieser Baustein als remanent definiert:<br> 1 = ja<br> 0 = nein<br> Ist der Baustein hier nicht als remanent gekennzeichnet, so sind als remanent gekennzeichnete Variablen trotzdem flüchtig (vgl. Satzart 5003).", "Anzahl der definierten Eingänge (mindestens 1 Eingang muss definiert sein)", "Alle Bezeichnungen der Eingänge. Enthält ein Baustein 4 Eingänge, werden vier Bezeichnungen benötigt.", "Anzahl der definierten Ausgänge (mindestens 1 Ausgang muss definiert sein)", "Alle definierten Ausgänge besitzen eine Bezeichnung. Pro Ausgang steht ein Feld zur Verfügung.", "Der hier angegebene Text wird im GLE als Versions-Nr. angezeigt."]
            inputCount = int(params[3])
            outputCount = int(params[4 + inputCount])

            if (inputCount > 0):
                paramDef.pop(4)
                descItem = paramDesc.pop(4)
                typeItem = paramType.pop(4)
                for i in range(1, inputCount + 1):
                    paramDef.insert(3 + i, "Bezeichnung Eingang " + str(i))
                    paramType.insert(3 + i, typeItem)
                    paramDesc.insert(3 + i, descItem)

            if (outputCount > 0):
                outputOffset = 4 + inputCount
                paramDef.pop(outputOffset + 1)
                descItem = paramDesc.pop(outputOffset + 1)
                typeItem = paramType.pop(outputOffset + 1)
                for i in range(1, outputCount + 1):
                    paramDef.insert(outputOffset + i, "Bezeichnung Ausgang " + str(i))
                    paramType.insert(outputOffset + i, typeItem)
                    paramDesc.insert(outputOffset + i, descItem)

        if (code == 4999):
            paramDef = ["Satzart", "Sprachkürzel", "Bezeichnung", "Bezeichnung Eingang n", "Bezeichnung Ausgang n"]
            paramType = ["Zahl", "Text", "Text", "Text", "Text"]
            paramDesc = ["Satzart", "2-stelliges Sprachkürzel der jeweiligen Sprache. Allgemein gilt: Für jede Sprache wird das TLD (TopLevel-Domain) Kürzel des Landes verwendet, in dem die Sprache beheimatet ist. Ausnahme: Englisch, da an vielen Stellen im HS/FS Experte historisch bereits das Kürzel en für Englisch verwendet wurde.", "Bezeichnung des Bausteins in der o.g. Sprache im HS/FS-Experte. Die Struktur im HS/FS-Experte ermöglicht eine Kategorisierung der Bausteine", "Alle Bezeichnungen der Eingänge. Enthält ein Baustein 4 Eingänge, werden vier Bezeichnungen benötigt.", "Alle definierten Ausgänge besitzen eine Bezeichnung. Pro Ausgang steht ein Feld zur Verfügung."]

        if (code == 5001):
            paramDef = ["Satzart", "Anzahl Eingänge", "Anzahl Ausgänge", "Anzahl Zeitspeicher", "Anzahl Speichervariablen", "Berechnung bei Initialisierung", "Kodierter Formel-Block (optional)"]
            paramType = ["Zahl", "Zahl", "Zahl", "Zahl", "Zahl", "Boolean", "Boolean"]
            paramDesc = ["Satzart", "Anzahl Eingänge", "Anzahl Ausgänge", "Anzahl Zeitspeicher", "Anzahl Speichervariablen", "Berechnung bei Initialisierung", "Kodierter Formel-Block (optional)"]

        if (code == 5002):
            paramDef = ["Satzart", "Eingang", "Init.-Wert", "Datenformat"]
            paramType = ["Zahl", "Zahl", "Zahl/Text", "Zahl"]
            paramDesc = ["Satzart", "Index des Eingangs, beginnend mit 1, fortlaufend", "Wert bei Initialisierung", "Format des Eingangs, 0 = Numerisch, 1 = Text"]

        if (code == 5003):
            paramDef = ["Satzart", "Speicher", "Init.-Wert", "Remanent j/n"]
            paramType = ["Zahl", "Zahl", "Zahl", "Boolean"]
            paramDesc = ["Satzart", "Index der Variable, beginnend mit 1, fortlaufend", "Wert mit dem die Variable initialisiert wird (dies kann ein Integer oder Float sein)", "Gibt an, ob der Wert der Variable remanent gepsiechert wird. Bei remanenter Speicherung bleibt der Wert der Variable auch nach dem Neustart erhalten. 1 = ja, 0 = nein.<br><br>Werden remanente Speichervariablen verwendet, muss dies in Satzart 5000 ebenfalls definiert sein. Ist in Satzart 5000 der Baustein nicht als remanent gekennzeichnet, so ist die Variable auch bei in diesem Feld gesetzter 1 nicht remanent."]

        if (code == 5004):
            paramDef = ["Satzart", "Ausgang", "Init.-Wert", "Runden auf binär", "Ausgang-Typ", "Datenformat"]
            paramType = ["Zahl", "Zahl", "Zahl/Text", "Boolean", "Zahl 1/2", "Zahl"]
            paramDesc = ["Satzart", "Der Index des Ausgangs. (Beginnend mit 1, fortlaufend)", "Wert mit dem der Ausgang initialisiert wird. Ist der Ausgang vom Typ Text, muss der Init.-Wert in Hochkommata gesetzt werden. Wichtig: Der Typ des Init.-Wertes und die Angabe im Feld Datenformat müssen identisch sein.", "Wandelt einen Wert in die Binärform (0 oder 1) um. Bei jedem Wert<>0 wird der Ausgang mit 1 belegt.<br> 1 = ja 0 = nein", "Send / Send by Change<br>1 = Berechnung (send). Hier wird der Wert bei jeder Berechnung auf den Ausgang gesendet.<br>2 = Bei Änderung (send by change). Hier wird der Wert nur dann auf den Ausgang gesendet, wenn der Wert am Ausgang sich dadurch ändern würde.", "Definiert das Format des Ausgangs.<br>0 = Numerisch (standard)<br>1 = Text Numerisch bedeutet Integer- oder Floatwert.<br>Ausgänge, welche als Text-Ausgang definiert werden, können im HS/FS-Experte nur mit K.-Objekten bzw. Eingängen belegt werden, welche ebenfalls vom Typ Text (z.B. 14 Byte) sind. Wichtig: Die Angabe des Datenformats ist nur für den HS/FS-Experte von Bedeutung. Der HS/FS erkennt das Datenformat anhand des Init.-Wertes. Datenformat und Init.-Wert müssen also im gleichen Format definiert werden."]

        if (code == 5012):    
            paramDef = ["Satzart", "Ende nach Ausführen j/n", "Bedingung", "Formel", "Zeitformel", "Pin-Ausgang"]
            paramType = ["Zahl", "Boolean", "Formel", "Formel", "Formel", "Zahl/Index"]
            paramDesc = ["Satzart", "Beendet die Berechnung des Bausteins, nach der Abarbeitung der Formel, wenn das Ergebnis der Bedingung ungleich Null ergibt.<br>1 = ja 0 = nein", "Wenn das Ergebnis der Bedingung ungleich Null ist wird die Berechnung der Formel ausgeführt. Soll das Ergebnis der Bedingung immer True/Wahr sein, so wird das Feld durch zwei Hochkommata gefüllt.", "Wird ausgeführt wenn Bedingung ungleich Null ergibt. Das Ergebnis der Berechnung kann auf die Pins weitergeleitet werden.", "Wird ausgeführt wenn Bedingung ungleich Null ergibt und min. ein Zeitspeicher im Baustein definiert wurde. Diese Angabe ist optional. Falls sie nicht benötigt wird sind Hochkommata zu setzen. Beispiel: Das Ergebnis dieser Berechnung dient dem im Pin Zeitspeicher zugewiesenen Zeitspeicher als Ausführungszeitpunkt. Der Ausführungszeitpunkt eines Zeitspeichers kann während einer Berechnung verändert werden. Siehe dazu auch Kapitel 6.", "In diesen Ausgang wird das Ergebnis der Berechnung im Feld Formel geschrieben. Die Angabe ist optional. Wenn dieser Wert gleich Null ist findet keine Weiterleitung an einen Ausgang statt."]

        for i in range(0, paramIdx):
            txt += paramDef[i] + " | "
        
        for i in range(paramIdx, len(paramDef)):
            if (i == paramIdx):
                txt += "<u>"

            txt += paramDef[i]

            if (i == paramIdx):
                txt += "</u>"
            
            if (i < len(paramDef) - 1):
                txt += " | "

        txt += "<br><br><strong>Datentyp: " + paramType[paramIdx] + "</strong>"
        txt += "<br>" + paramDesc[paramIdx]
                

        return txt
    
    def run(self, edit):
        import re
        view = self.view

        scope = view.scope_name(view.sel()[0].b)
        
        extension = view.file_name().split(".")[-1]

        if (extension != 'hsl') and (extension != 'py'):
            return
        
        for region in view.sel():
            # Only interested in empty regions, otherwise they may span multiple
            # lines, which doesn't make sense for this command.
            if region.empty():
                pos = view.rowcol(region.begin())           
                posx = pos[1]

                # Expand the region to the full line it resides on, excluding the newline
                line = view.line(region)
                lineContents = view.substr(line)

                paramIdx = lineContents[:posx].count("|")

                lineContents = lineContents.strip()
                commentpos = lineContents.find('#')
                if (commentpos > 0):
                    lineContents = lineContents[:commentpos]
                
                m = re.compile('[0-9]*\|.*')
                if (m.match(lineContents)):
                    idx = lineContents.find('|')
                    code = lineContents[:idx]   
                    params = lineContents.split('|')
                    title = self.getHelpTitle(code)
                    desc = self.getHelpText(int(code), params, paramIdx)
                    view.show_popup(self.css + '<h1>' + code + " - " + title + '</h1>'+ desc, location=-1, max_width=600)