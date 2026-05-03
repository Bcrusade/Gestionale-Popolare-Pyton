#!/bin/bash

# Verifica se Python è installato
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Python non è installato. Installazione in corso..."
  
  # Scarica l'installer di Python (per macOS sarebbe un'installazione manuale, quindi questo passo è per riferimento)
  #curl "https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe" -o python-installer.exe
  
  # macOS di solito utilizza Homebrew per l'installazione di software
  if ! command -v brew > /dev/null; then
    echo "Homebrew non è installato. Installazione in corso..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  
  brew install python3
else
  echo "Python è installato."
fi

# Crea un ambiente virtuale
cd ..
python3 -m venv venv
source ./venv/bin/activate

# Installa Flask
pip install -U Flask

# Disattiva l'ambiente virtuale
deactivate

cd - > /dev/null

# macOS non richiede una fase di eliminazione dell'installer poiché non scarichiamo un file eseguibile.
# Inoltre, non c'è un comando equivalente a "RefreshEnv.cmd" poiché le variabili d'ambiente sono gestite in modo diverso.

echo "Operazioni completate. Premere un tasto per continuare..."
read -n 1
