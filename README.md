---
title: "README"
---

# EBM veiledning for utviklere og avanserte brukere

Dette er en instruks for hvordan man kommer i gang med EBM modellen. Det er et par steg man må gjennføre før man kan kjøre skriptene i EBM modellen. Stegene er som følger:

1. *Clone* et repository fra Energibruksmodellen på Azure Devops 
2. Opprette eget Virtuel Environment (*venv*) i prosjektmappen
3. Opprette *.env* fil med nødvendige miljøvariabler
4. Oppdater innstillinger i VS code 

Du trenger kun å gjennomføre dette når du kloner et repository (*repo*) til arbeidsmappen din. Etter du har klonet repo den første gangen, så kan du bytte til ny branch i VS code og beholde de nødvendige filene og instillingene du trenger for å kjøre skript. Stegene er de samme uavhengig av om man jobber lokalt eller på e-srv, men dersom man jobber lokalt må man også installere nødvendige programmer først. Hvis du ikke har installert nødvendige programmer lokalt, så gjennomfør stegene i den veiledningen først.

---

### Clone Repository

Du kan "klone" et repository (*repo*) fra Energibruksmodellen på Azure DevOps på to måter. Enten direkte fra VS Code eller via Azure DevOps. Før du kloner et repo burde du opprette en mappe som vil fungere som ditt arbeidsted eller "workspace" for prosjektet. Kall gjerne denne mappen for "work_space", og plasser repositoriet i denne mappen. 

#### Klone via VS code

1. Åpne VS code og klikk på Source Control (*Ctrl + Shift + g*) <br>  
    ![source control](\images\source_control.png) 
    <br>
    
2. Velg "Clone Repository" og bruk filstien fra DevOps <br>
    ![clone repo](\images\clone_repo.png)
    <br>
 
    ![repo path](\images\repo_filsti.png)
    <br>
3. Plasser klonet repo i din arbeidsmappe.<br>
    ![folder placement](\images\folder_placement.png)
    <br>

#### Klone via DevOps

1. Åpne Azure DevOps og velg ønsket repo. Tykk på "Clone".<br>
    ![devops](\images\devops1.png)
    <br>

2. Velg "Clone in VS code" og plasser repo i arbeidsmappen din.<br> 
    ![devops](\images\devops2.png)
    <br>

---

### Opprett Virtual Environment

1. Åpne terminalen i VS Code og bruk kommandoen ``python -m venv .venv``. ``.venv`` definerer navnet på virtual environment mappen og dette kan endres, men er ikke anbefalt. ``python`` kan endres til filtsi for python versjonen du ønsker å bruke, for eksempel: ``C:\Users\lfep\work_space\Energibruksmodell\.venv\Scripts\python.exe -m venv .venv``. Dersom ``python`` brukes så velges automatisk default python versjon. For å kunne kjøre pakkene som brukes av EBM trengs minst python 3.10 eller nyere. Du kan sjekke hvilken python versjon som blir brukt ved å kjøre kommondoen ``python --version``<br> 
![create venv](\images\create_venv.png) <br>
![python version](\images\python_version.png)
<br>

2. Plasser det nyopprettede Virtual Environmentet i arbeidsmappen din. Det burde komme opp en melding som vist på bildet nedenfor. <br>
    ![folder](\images\venv_folder.png)
    <br>

3. Velg Python Interpeter som følger med ditt nyopprettede Virtual Enviornmentet. Trykk på ``Shift + Controil + P`` for å åpne Command Palette og velg ``Python: Select Interpeter``. Deretter velg Virtual Environmentet som du opprettet fra dropdown menyen, eller gi filtsien til python interpeteren dersom den ikke dukker opp, for eksempel slik: ``X:\Brukere-felles\lfep\work_space\Energibruksmodell\.venv\Scripts\python.exe``.
<br>

4. Aktiver Virtual Environmentet ditt med følgende kommando: ``.venv\Scripts\activate.ps1``.<br>
![activate venv](\images\activate_venv.png)
<br>

5. Installere nødvendige libraries med følgende kommando: ``python -m pip install -r requirements.txt``. Dette installerer nødvendige pakker som brukes av EBM modellen, som vist på bildet nedenfor.<br>
![install libraries](\images\install_libraries.png) imp
<br>

---

### Opprett *.env* fil

For at EBM modellen skal fungere trengs det en *.env* fil. I denne filen definerer man nødvendige miljøvariabler. For mer om *.env* filer se f.eks. denne [lenken](https://www.geeksforgeeks.org/how-to-create-and-use-env-files-in-python/). 

1. Opprett en *.env* fil i roten av directory-et du arbeider i.<br>
![env fil](\images\env_file.png)
<br>

2. Definerer miljøvariabelen ``PYTHONPATH=<location/path for workspace folder>``. Hvis arbeidsmappen din heter "work_space" så skal filstien se ut som dette: ``PYTHONPATH=x:\Brukere-felles\lfep\work_space\Energibruksmodell``. 
<br>

3. Definer miljøvariabelen ``DEBUG``. Denne kan enten settes til ``DEBUG=True`` eller ``DEBUG=False``, avhengig av om man ønsker å vise debug meldinger eller ikke. For at debug meldinger ikke skal vises trenger man fremdeles å definere det i koden med *if statement*. 
<br>

4. Dersom du ønsker å kjøre skripts som sammenligner EBM resultater med tall i BEMA modellen, så trenger du å definere miljøvariabelen ``BEMA_SPREADSHEET``. Her definerer du filstien til BEMA excel-filen som kun inneholder verdier og ingen formler. For en kopi av denne modellen ta kontakt med Ketil eller Lars F. Variabelen defineres f.eks. slik: ``BEMA_SPREADSHEET=X:\Brukere-felles\lfep\BEMA\qqBEMA_2019-uten-formler.xlsm``.
<br>

5. Husk å lagre filen! Den skal se slik ut (hvis du har med alle variabler):<br>
![env vars](\images\env_variables.png)
<br>

6. Det kan være at du må oppdatere instillingene dine i VS code for at det skal fungere. Dette er nok tilfelle hvis du får følgende feilmelding når du prøver å kjøre en av skriptene i EBM modulen: ``ModuleNotFoundError: No module named 'ebm'``. VS code kan være litt vrient å ha med å gjøre og vi er litt usikre på nøyaktig beste framgangsmåte for å løse dette. Prøv å legge til en ``settings.json`` fil under mappen .vscode med følgende kode: 

     ```json   
    {
    "python.terminal.activateEnvInCurrentTerminal": true,
    }
    ```
    Dersom dette ikke fungerer, ta kontakt med Ketil for hjelp.  

---

### Nedlasting av programmer for å arbeide lokalt

Dette gjelder kun dersom du skal arbeide lokalt og ikke på e-srv. 

1. Last ned programvarer via Firmaportalen. Dersom de ikke er tilgjengelig på firmaportalen eller nedlasting feiler, prøv å laste ned via Microsoft Store / nett eller ta kontakt med brukerstøtte. Du trenger å laste ned følgende programmer:

    - Visual Studio (VS) code
    - Python
    - Git (Git for Windows)
<br>

2. Restart PCen etter installasjonene er fullført. Det er ofte de ikke fungerer første gang.
<br>

3. Etter VS Code og Python er installert. Åpne VS code og installer følgende extensions:
    - Python (Pylance og Python Debugger følger også med) 
    - Bookmarks (Ikke must, men praktisk)
    - Excel Viewer (Ikke must, men praktisk for å se input csv.filer)
<br>

4. (Valgfritt) Logg inn og sync instillinger i VS code. Anbefales, da instillingene dine vil bli lagret på profilen din. 
    - Velg "Account" nederst i venstre hjørne
    - Trykk på "Backup and sync settings"
    - Logg inn med Microsoft kontoen din
