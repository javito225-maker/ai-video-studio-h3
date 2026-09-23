#!/usr/bin/env bash
set -euo pipefail

COMFY_DIR="${COMFY_DIR:-/mnt/comfy/ComfyUI}"
STUDIO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$STUDIO_DIR/workflows/h3_t2v.json"

echo "=== Configuration MiniMax H3 local ==="
echo "ComfyUI: $COMFY_DIR"

if [ ! -d "$COMFY_DIR" ]; then
  echo "ERREUR: ComfyUI introuvable dans $COMFY_DIR"
  echo "Relance avec: COMFY_DIR=/chemin/vers/ComfyUI ./setup-h3.sh"
  exit 1
fi

mkdir -p "$STUDIO_DIR/workflows"

echo
echo "1. Mets ComfyUI à jour (H3 natif exige une version récente)."
echo "2. Dans ComfyUI: Template Library > Video > MiniMax H3 > Text-to-Video."
echo "3. Suis le téléchargement des modèles proposé par ComfyUI."
echo "4. Active les options développeur puis exporte le workflow au format API."
echo "5. Sauvegarde/copie ce fichier ici:"
echo "   $TARGET"
echo
echo "Quand le fichier existe, ce script le valide automatiquement."

if [ ! -f "$TARGET" ]; then
  echo
  echo "ETAT: workflow API H3 manquant."
  exit 2
fi

python3 - "$TARGET" <<'PY'
import json, sys
p=sys.argv[1]
with open(p, encoding="utf-8") as f:
    w=json.load(f)
if not isinstance(w, dict) or not w:
    raise SystemExit("ERREUR: JSON workflow vide/invalide")
nodes=[v for v in w.values() if isinstance(v,dict)]
classes=[str(n.get("class_type","")) for n in nodes]
h3=[c for c in classes if "MiniMaxH3" in c or "minimax_h3" in c.lower()]
if not h3:
    raise SystemExit("ERREUR: aucun noeud MiniMax H3 natif trouvé. Exporte bien le workflow API H3.")
print("OK: workflow H3 API valide.")
print("Noeuds H3:", ", ".join(sorted(set(h3))))
PY

echo
echo "Configuration H3 prête."
echo "Redémarre AI Video Studio H3 puis clique Vérifier système."
