"""Pubblica i risultati per l'app Tribuna.

Uso:
  python3 aggiorna.py --stato     stampa, per ogni campionato già pubblicato, id e updatedAt
  python3 aggiorna.py nuovi       unisce i file nuovi/<id>.json in aggiornamenti.json
                                  (vince l'updatedAt più recente), controlla i dati e riscrive il file

Ogni file nuovi/<id>.json contiene un campionato: {"updatedAt", "asOf", "fonte", "rows", "rounds"}.
"""
import json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(HERE, "aggiornamenti.json")
ID = re.compile(r"^[a-z0-9-]{2,40}$")


def load():
    try:
        with open(FILE, encoding="utf-8") as f:
            j = json.load(f)
        return j.get("aggiornamenti") or {}
    except FileNotFoundError:
        return {}


def check(cid, d):
    """Restituisce un messaggio d'errore, oppure None se il campionato va bene."""
    if not ID.match(cid):
        return "id non valido"
    if not isinstance(d, dict):
        return "non è un oggetto"
    if not isinstance(d.get("updatedAt"), (int, float)) or d["updatedAt"] < 1.7e12:
        return "updatedAt mancante o non in millisecondi"
    rows, rounds = d.get("rows"), d.get("rounds")
    if rows is None and not rounds:
        return "mancano sia rows sia rounds"
    if rows is not None:
        if not isinstance(rows, str) or not rows.strip():
            return "rows non è testo"
        lines = rows.strip().split("\n")
        if len(lines) < 2:
            return "classifica con meno di 2 squadre"
        names = set()
        for ln in lines:
            c = ln.split("|")
            if len(c) < 3 or not c[0].strip():
                return "riga di classifica non valida: " + ln[:60]
            if c[0] in names:
                return "squadra ripetuta: " + c[0]
            names.add(c[0])
            for x in c[1:8]:
                if x.strip() and not re.match(r"^-?\d{1,3}$", x.strip()):
                    return "numero non valido nella riga: " + ln[:60]
    if rounds is not None:
        if not isinstance(rounds, list):
            return "rounds non è una lista"
        for r in rounds:
            if not isinstance(r, dict) or not isinstance(r.get("m"), list):
                return "giornata non valida"
            for m in r["m"]:
                if not isinstance(m, dict) or not m.get("h") or not m.get("a"):
                    return "partita non valida in " + str(r.get("name"))
    return None


def save(docs):
    body = ",\n".join(json.dumps(k, ensure_ascii=False) + ":" + json.dumps(docs[k], ensure_ascii=False, separators=(",", ":")) for k in sorted(docs))
    text = '{"versione":1,"scritto":%d,"aggiornamenti":{\n%s\n}}\n' % (int(time.time() * 1000), body)
    json.loads(text)  # deve restare JSON valido
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    docs = load()
    if sys.argv[1] == "--stato":
        for k in sorted(docs):
            print(k, docs[k].get("updatedAt"))
        return 0
    folder = os.path.join(HERE, sys.argv[1]) if not os.path.isabs(sys.argv[1]) else sys.argv[1]
    changed, skipped = [], []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json"):
            continue
        cid = name[:-5]
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                d = json.load(f)
        except Exception as e:  # file scritto male
            skipped.append(f"{cid} (JSON non valido: {e})")
            continue
        err = check(cid, d)
        if err:
            skipped.append(f"{cid} ({err})")
            continue
        old = docs.get(cid)
        if old and old.get("updatedAt", 0) >= d["updatedAt"]:
            skipped.append(f"{cid} (già pubblicato)")
            continue
        docs[cid] = d
        changed.append(cid)
    if changed:
        save(docs)
    print("Aggiornati:", ", ".join(changed) or "nessuno")
    if skipped:
        print("Saltati:", "; ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
