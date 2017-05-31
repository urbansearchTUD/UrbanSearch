import time
from modelmanager import ModelManager


mm = ModelManager(filename='sgdcmodel.pickle')

doc_onderwijs = """
    Wat is nodig om de verschillen tussen scholen weg te werken?
    Betere leerkrachten, vinden twee deskundigen.
    De verschillen tussen scholen zijn te groot,
    constateerde de Inspectie van het Onderwijs deze week.
    Dat kan alleen opgelost worden met extra geld vanuit Den Haag,
    reageren de koepelorganisaties. Is dat inderdaad de oplossing voor
    de grote verschillen tussen scholen? En wat kunnen scholen die volgens
    de inspectie achterblijven, doen om het beste uit hun leerlingen te halen?

    Alles staat of valt met de kwaliteit van de leerkracht, zegt
    universiteitshoogleraar Paul Kirschner van de Open Universiteit.
    Kirschner heeft veel onderzoek gedaan naar wat wel en niet werkt in de klas.
    "We kennen allerlei technieken die bewezen effectief zijn.
    Op scholen waar die technieken worden gebruikt, wordt
    aantoonbaar beter onderwijs gegeven."

    Het probleem is: lang niet alle scholen en leraren kennen die technieken.
    Sterker nog, leerkrachten gebruiken volgens Kirschner nog te
    vaak trucjes en methodes die aantoonbaar onzinnig zijn.
    "Om goed onderwijs te geven moet een docent zijn vak beheersen."

    Tekst loopt door onder afbeelding.


    Er is extra geld nodig om verschillen tussen scholen te verkleinen.
    En daar schort het volgens hem nog wel eens aan.
    Nederland is een van de weinige rijkere industrielanden waar een
    meerderheid van de leerkrachten geen universitair diploma heeft.
    Als het aan Kirschner ligt verandert dat. Hij wil dat elke docent
    academisch wordt opgeleid.

    Zo bezien is er inderdaad extra geld nodig om de verschillen
    tussen scholen te verkleinen. Voor nieuwe lerarenopleidingen en voor
    betere salarissen. Kirschner:
    "Je moet het wel zo inrichten dat een onderwijscarrière aantrekkelijk is."

    Van onderzoeker Erna van Koeven, verbonden aan het lectoraat
    Pedagogische kwaliteit van het onderwijs van Hogeschool Windesheim,
    hoeft niet elke leerkracht academisch geschoold te zijn. Maar ook zij
    hamert op het belang van goede docenten. "Op scholen die het beste uit
    hun leerlingen halen, werken leraren veel samen en krijgen ze de tijd
    om van elkaar te leren."

    Die tijd moet er wel zijn. Nederlandse leerlingen zitten veel uren
    in de klas, waardoor docenten weinig tijd hebben om zelf
    onderwijs te volgen. "In Finland, en daar kijken we toch vaak naar,
    zitten kinderen minder lang in de klas dan hier", zegt Van Koeven.
    "Daardoor hebben leraren meer tijd voor hun eigen ontwikkeling."
    Extra geld helpt om tijd te kopen, zegt Van Koeven.

    Of daar werkelijk iets zinnigs mee gebeurt,
    hangt dan weer af van iets moeilijk definieerbaars als
    de cultuur op een school.

    "Voor mij is het belangrijkste het vertrouwen dat ik voel",
    zegt leraar van het jaar Daisy Mertens. Ze geeft les aan groep
    zeven van De Vuurschool in Helmond, een multiculturele school
    met leerlingen die gemiddeld een hogere score behalen op de
    eindtoets dan vergelijkbare scholen.

    "Ons lerarenteam is heel erg bezig met de ontwikkeling van ons vak",
    is haar verklaring daarvoor. "Onze schoolleider is daarin erg belangrijk.
    Hij vertelt ons niet wat we moeten doen maar spreekt wel ambities uit
    en geeft ons de ruimte voor ontwikkeling."

    Hogere salarissen of kleinere klassen zijn volgens de leraar
    van het jaar twee van de manieren om het onderwijs te verbeteren.

    "Maar we moeten goed kijken wat werkt en waar behoefte aan is.
    Leraren moeten verantwoordelijkheid krijgen,
    maar nog belangrijker is dat ze die ook nemen.
    We mogen best wat meer vechten voor ons vak", aldus Mertens.
    """

doc_dh = """
    Trek de regels gelijk en de detailhandel in de Benelux gaat er met rasse
    schreden op vooruit.
    De detailhandel in België, Luxemburg en Nederland komt door de
    huidige regelgeving niet tot zijn recht, concluderen onderzoekers van de
    Vlerick Business School in het rapport ‘Benelux Detailhandel 2025’.
    Trekken de overheden van de drie landen hun beleid gelijk, dan kan dat
    95.000 extra banen en 23 miljard euro meer omzet opleveren.
    Over krap acht jaar zouden die resultaten al behaald kunnen worden,
    menen de onderzoekers.

    De belemmerende regelgeving komt voor op allerlei fronten van de
    detailhandel, zegt Margriet Keijzer, secretaris Europa bij
    branchevereniging Detailhandel Nederland. Sommige producten die in
    Nederland legaal in de schappen staan, mogen er in Belgische supermarkten
    niet in. “In België mag je chocomelk alleen chocomelk noemen als het
    van gesmolten chocolade is gemaakt. In Nederland mag dat ook als het van
    cacaopoeder is gemaakt”, legt Keijzer uit. En ook de naam van een product
    kan problematisch zijn als je het als winkelier over de grens wil verkopen.
    “Lippenstift Lipstick noemen in België mag niet, want daar zijn
    Engelse termen op producten verboden.”

    Die verpakkingen aanpassen of de producten anders noemen,
    brengt extra kosten met zich mee, zegt Keijzer.
    En het zorgt ervoor dat winkeliers die in eigen land goed boeren
    niet snel over de grens zaken willen doen. “Ze moeten een degelijke
    studie ondergaan willen ze in andere landen actief zijn. Die complexe
    regelgeving weerhoudt ze ervan de stap naar het buitenland te maken.”

    Verschuiving naar online
    Retaildeskundige Cor Molenaar betwijfelt of het gelijktrekken van
    de regelgeving in de Benelux de detailhandel zoveel oplevert.
    “Een omzet van 23 miljard extra? Ik geloof er niks van.
    Er is geen sprake van een groeiende vraag, maar van een verschuivende vraag.
    Als ik nu door Roermond wandel, zie ik Belgen die er graag shoppen.
    Wordt België goedkoper, dan gaan de Nederlanders daar shoppen.”

    Het probleem waar de detailhandel nu mee kampt, ligt heel ergens anders,
    zegt Molenaar. “Klanten komen minder naar de winkel en kopen steeds meer
    online.” En de conservatieve winkeliers spelen te weinig in op dat nieuwe
    koopgedrag om klanten weer de winkel in te krijgen, stelt Molenaar.
    “Consumenten willen niet altijd betalen voor parkeren, willen ook op
    zondag kunnen winkelen, of na zes uur kunnen shoppen. Of ze willen dat
    hun producten thuis bezorgd worden. Winkeliers vinden dat soms lastig.”

    Kiezen de drie overheden er dan toch voor om de regelgeving gelijk te
    trekken, dan moeten ze dat doen vanuit de visie van de consument,
    adviseert Molenaar. Een voorbeeld: wil een Nederlander bij een Vlaamse
    webshop iets bestellen, dan moet ook dat een dag later binnen kunnen zijn.
    """

doc_3 = """
    De Digitale Interne Markt: veel goede intenties, weinig concrete resultaten

    Twee jaar na de introductie van een van haar belangrijkste vlaggenschepen, de strategie voor de digitale interne markt, maakt de Europese Commissie de balans op. Hoe staat het met de creatie vaneen digitale interne markt, waar het voor burger en ondernemer “grensoverschrijdend net zo makkelijk opereren is als in het eigen land”? Volgens Detailhandel Nederland zijn de intenties veelbelovend, maar zal nog veel meer moeten worden gedaan om ze daadwerkelijk te realiseren.
    Voor Detailhandel Nederland zijn de prioriteiten duidelijk: aanpakken van handelsbarrières, zoals het verschil in consumentenbescherming en vereenvoudiging van grensoverschrijdende BTW-procedures.

    Een digitale interne markt is broodnodig voor winkeliers. Nog te vaak remmen de verschillen in nationale regels onnodig de grensoverschrijdende handel. Daarom was Detailhandel Nederland blij met voorstellen om die verschillen eindelijk aan te pakken. Ondertussen blijkt echter dat de focus op de verkeerde onderwerpen lag of dat de Europese lidstaten niet over hun eigen schaduw heen durfden te stappen en de verschillen tussen hun landen echt te willen opheffen. Het besef mist dat de digitale interne markt en de fysieke interne markt niet van elkaar gescheiden kunnen worden.

    Zo is de maatregel om grensoverschrijdende geoblocking aan te pakken door de Europese Commissie verheven tot een van de belangrijkste speerpunten uit de digitale interne markt. Door het voorstel moeten de 500 miljoen potentiële klanten online kunnen winkelen, waar ze maar willen in Europa. Een fantastische kans, maar niet realistisch zolang winkeliers niet met vertrouwen over de grens kunnen verkopen. Producten moeten nog altijd fysieke grenzen over, waar ze moeten voldoen aan verschillende regelgeving rond bijvoorbeeld consumentenbescherming, ingewikkelde procedures voor btw-aangifte, en verschillen in etiketteringen en verpakkingen.

    Het voorstel voor het gelijktrekken van regels rond consumentenkopen is een enorme kans voor Europa, haar winkeliers en consumenten. Door bijvoorbeeld een gelijke garantietermijn in 28 lidstaten te hanteren wordt regelgeving duidelijk, eerlijk, en minder belastend. In de praktijk blijkt het erg moeilijk om stappen te maken. Alhoewel maar liefst 21 van de 28 lidstaten dezelfde garantietermijn hanteren (2 jaar) blijkt het politiek zeer moeilijk om op alle aspecten van consumentenkoop tot een gemeenschappelijk systeem te komen. Landen met een hoger niveau van consumentenbescherming dan het gemiddelde, zijn niet bereid daarin concessies te doen, zelfs als die leiden tot meer consumentenkeuze en een beter concurrerende sector. Een echte digitale interne markt betekent voordelen voor iedereen, maar dan moeten beleidsmakers wel water bij de wijn durven doen.

    De voorstellen voor vereenvoudiging van btw-procedures zijn minstens zo belangrijk. Een online alles-in-één-loket kan de administratieve lasten en kosten bij grensoverschrijdend zakendoen aanzienlijk verminderen. Daarnaast wordt het gelijke speelveld flink verbeterd door de btw-vrijstellingen af te schaffen voor producten direct geïmporteerd uit derde landen. Al vanaf 2021 zouden winkeliers kunnen profiteren van deze maatregelen, maar dan moeten de lidstaten wel hun verantwoordelijkheid durven nemen en deze voorstellen zo snel mogelijk uitvoeren.

    Uit eigen onderzoek blijkt dat een op de vijf winkeliers graag offline en/of online wil groeien over de grens, maar dit niet doet door uiteenlopende regels. Detailhandel Nederland roept de Europese Commissie, het Europees Parlement, en de nationale overheden op om hun verantwoordelijkheid te nemen om de afspraken voor een interne markt waar te maken.  Hierdoor ontstaat meer concurrentie, meer innovatie en een nog beter assortiment tegen scherpere prijzen.
    """

doc_4 = """
    De detailhandel zette in januari 0,8& procent meer om dan in
    januari 2013. De verkochte artikelen waren 0,2 procent duurder dan een
    jaar eerder. Het volume van de omzet was 0,6 procent groter.
    De samenstelling van de koopdagen was in januari dit jaar gunstiger
    dan in januari 2013. Het opwaartse effect hiervan op de omzet
    wordt geraamd op ongeveer 1 procent. Winkels in de food-sector behaalden
    2,1 procent meer omzet. De omzet van de supermarkten nam minder
    hard toe dan die van de speciaalzaken.
    De prijzen in de food-sector stegen met 1,4 procent,
    het volume van de omzet was 0,8 procent groter.
    De omzet van de winkels in de non-foodsector lag op hetzelfde niveau als
    een jaar eerder, net als de prijzen van de verkochte artikelen
    en het volume. Binnen de non-foodsector liep het beeld uiteen.
    Winkels in consumentenelektronica, doe-het-zelfzaken, woninginrichters,
    textielsupermarkten en drogisterijen behaalden minder omzet.
    Winkels in bovenkleding zetten daarentegen flink meer om.
    De omzet van winkels in huishoudelijke artikelen was iets hoger dan
    een jaar eerder. Het overgrote deel van de detailhandelsomzet
    wordt gegenereerd door ondernemers met een winkel. De winkels in de
    non-food-sector waren in 2013 goed voor 48 procent van de totale
    detailhandelsomzet. Het aandeel van winkels in de foodsector kwam uit
    op 37 procent. Tankstations droegen 9 procent bij en de detailhandel
    niet-in-winkel zorgde voor de resterende 6 procent.
    Tot de detailhandel niet-in winkel behoren ook bedrijven die hoofdzakelijk
    via postorder en/of internet aan consumenten verkopen.
    Deze bedrijven presteren al geruime tijd beter dan de winkels.
    In januari was hun omzet 7,2 procent hoger dan een jaar eerder.
    """

doc_shop = """
    Dat mannen niet dol zijn op shoppen zal velen niet vreemd in de oren klinken.
    Er is nu een Instagram-account dat hier heel grappig op inspeelt.

    Veel vrouwen zijn dol op winkelen, veel mannen vinden het daarentegen
    een stuk minder leuk als ze mee moeten shoppen. Dit Instagram-account
    plaatst foto’s van mannen die zich rot vervelen tijdens het winkelen.
    De foto’s worden geplaatst onder het account van @miserable_men.

    Dat levert onder andere deze hilarische beelden op:
    """

doc_verhuizing = """
    Logo van de gemeente Leusden

    Zoeken

    HomeBouwen en wonenVerhuizenVerhuizen naar en binnen Leusden
    Verhuizen naar en binnen Leusden
    Als u naar Leusden of binnen Leusden verhuist, geeft u dit door aan de gemeente. Dit kan 4 weken voor en uiterlijk 5 werkdagen na de verhuizing. U wordt automatisch uitgeschreven uit uw vorige gemeente. U ontvangt een bevestigingsbrief op uw nieuwe adres. Alle (semi)overheidsinstanties waarmee u een relatie heeft, krijgen een verhuisbericht.
    Verhuizing doorgeven
    Is online doorgeven voor u niet mogelijk, maak dan digitaal een afspraak om uw verhuizing in het gemeentehuis door te geven. Meenemen:

    een geldig identiteitsbewijs
    uw nieuwe adresgegevens
    Wie kan de verhuizing doorgeven
    Uzelf, als u 16 jaar of ouder bent.
    Samenwonende echtgenoten of geregistreerd partners: voor elkaar.
    Ouder, voogd of verzorger: voor hun kinderen jonger dan 16 jaar.
    Ouders en hun meerderjarige kind(eren) mogen de verhuizing voor elkaar doorgeven, als ze op hetzelfde adres wonen.
    Curator: voor een persoon die onder curatele is gesteld.
    Hoofd van een zorginstelling: voor iemand die in een zorginstelling gaat wonen
    Partners die niet getrouwd zijn of geen geregistreerd partnerschap hebben, moeten zelf aangifte van de verhuizing doen.
    Contact met de gemeente
    U bent welkom in het gemeentehuis in Leusden. Wij werken op afspraak, zodat wij u snel kunnen helpen.
    Afspraak maken
    gemeente@leusden.nl
    Fokkerstraat 16, 3833 LD Leusden
    Openingstijden milieustraat
    Vandaag: geopend van 08:30 uur tot 13:00
    Morgen: gesloten
    Proclaimer en privacyColofonUw reactieSitemapBekendmakingenToegankelijkheidCookiesContact
    TwitterFacebookYoutube
    """

doc_vh_2 = """
    Verhuizen lijkt eigenlijk helemaal niet zo duur te zijn. Tenslotte neem je gewoon al je spullen mee van het ene naar het andere huis. Natuurlijk veranderen je maandlasten, maar afgezien daarvan lijkt het allemaal nogal mee te vallen. Toch klagen veel mensen ongeveer een jaar na de verhuizing, dat die toch heel wat meer kostte dan ze dachten. Hoe komt dat? Hoe duur is het eigenlijk om te verhuizen?

    1. Voorbereidingen en inpakken
    Allereerst ga je natuurlijk je voorbereidingen treffen en je spullen inpakken. Dat lijkt goedkoop, maar je bent al snel best wat geld kwijt aan goede dozen en verpakkingsmateriaal. Doe je het goedkoop, dan haal je dozen uit de supermarkt of vraag je kennissen of zij nog dozen over hebben. Vaak heb je dan allemaal verschillende dozen met andere formaten, of dozen die niet (meer) stevig genoeg zijn. Het verpakken van serviesgoed lukt ook met oude kranten, maar voor bijvoorbeeld kunstwerken is het wel belangrijk dat je verpakkingsmateriaal aanschaft. Al met al kun je het beste zo’n €100,- opzij zetten voor het inpakken van je spullen.

    2. Het echte verhuizen
    Het echte verhuizen gebeurt meestal met een vrachtwagen of bus. Deze moet gehuurd worden en als je een grote vrachtwagen bestelt moet je natuurlijk ook de chauffeur betalen. Toch is dit wel de voordeligste manier van verhuizen. Uit berekeningen blijkt dat “gratis” verhuizen met een aanhanger of alleen auto’s uiteindelijk duurder is omdat meubels sneller beschadigd raken tijdens het in- en uitladen en tijdens het vervoer. Een verhuisbedrijf lijkt een dure optie, maar is meestal toch het goedkoopst omdat je spullen snel, praktisch en onbeschadigd worden verhuisd.
    3. Klussen in de nieuwe woning
    De nieuwe woning is vrijwel nooit helemaal kant-en-klaar. Zelfs in een mooi nieuw huis wil je vaak nog even behangen, schilderen of een vloer vervangen. De kosten gaan natuurlijk serieus oplopen als je een nieuwe keuken of badkamer moet plaatsen of als je de woning wilt verbouwen. Hou hier rekening mee in het verhuisbudget. Als je bijvoorbeeld een muur wilt schilderen, zal je ook rekening moeten houden met het kopen van kwasten, verfbakjes en andere benodigdheden. Deze kostenpost wordt door de meeste mensen die verhuizen echter wel vrij goed ingeschat.
    4. Nieuwe meubels en decoraties
    Eenmaal in je nieuwe huis, is er vaak een vrij onverwachte kostenpost: je gaat shoppen voor nieuwe meubels en decoraties. Dat betekent niet dat je al je meubels ineens vervangt, maar wel blijkt vaak dat je toch minstens 3 grote meubels vervangt als je gaat verhuizen. Dat kan ook zijn omdat je kleerkast niet meer past of als je ineens extra ruimte krijgt en graag wat extra meubels wilt neerzetten. Daarnaast vervang je meestal ook decoraties, waardoor de kosten heel geleidelijk ook aardig kunnen oplopen.
    5. Tuinklussen
    Bij het verhuizen is de tuin eigenlijk vrijwel nooit helemaal jouw smaak. Misschien is hij betegeld, maar wil jij liever een beplante tuin. Of staat de tuin juist vol groen terwijl jij een onderhoudsarme tuin wilt. Bereken van tevoren de kosten die de tuin met zich meebrengt. Het laten aanleggen van een tuin door een professional kan duur zijn, maar is in veel gevallen goedkoper dan het helemaal zelf doen. Het bespaart je namelijk niet alleen veel tijd, maar de tuinman kan ook de beplanting en tegels goedkoper leveren.
    Verhuizen lijkt in principe niet duur, maar dat komt vooral omdat er veel kosten niet worden meegerekend. Veel van de kosten hangen af van wat je wilt en welk huis je koopt. Hou altijd een budget apart voor onverwachte kosten en tegenvallers. Zo kan het huis dat je koopt verborgen gebreken hebben of gaat er iets mis tijdens de verhuizing wat extra geld kost. Wanneer je zeker weet dat je ook eventuele tegenvallers kunt dekken, kun je een stuk rustiger aan je verhuizing beginnen.
"""

doc_vh_3 = """
    Of u nou een woning wilt gaan kopen of huren, aan beide mogelijkheden zitten zowel voor als nadelen. Wij hebben de voor en nadelen eens voor u op een rijtje gezet

    Kopen
    Een voordeel van een kopen is de vermogensgroei die de consument ermee kan realiseren. Na twintig tot dertig jaar is het huis meestal afbetaald en wordt het eigen bezit. Daarnaast is kopen fiscaal aantrekkelijk, omdat de rente aftrekbaar is. Een huis is over het algemeen ook een waardevaste belegging. Het kan zelfs enorm in waarde toenemen. Een nadeel van een eigen huis is de onzekerheid over de rentestand na afloop van de rentevaste periode. Na tien jaar kan de rente procentpunten hoger liggen, waardoor de maandelijkse woonlasten zullen stijgen. Daarnaast is de onroerende zaakbelasting hoger dan bij een huurhuis en moet het eigenwoning-forfait worden betaald. Ook zijn reparaties en onderhoud aan het huis voor eigen rekening. Die kosten komen bij een huurhuis voor rekening van de verhuurder of woningcorporatie.


    Huren
    Opzeggen van de huur is makkelijker dan de verkoop van een huis en de huurder kan opzeggen wanneer hij wil. De maandelijkse lasten zijn in het algemeen wat lager en zijn reparaties en onderhoud voor kosten van de verhuurder. Ook mogen huurders sinds kort verbouwingen uitvoeren in hun huurwoning. Als ze vertrekken hoeven ze het huis, in tegenstelling tot voorheen, niet meer in de oude staat op te leveren. Bij huren is er geen sprake van vermogensgroei. De huur kan jaarlijks stijgen en de keuze van woning en locatie is soms beperkt. Verder kan de huurder te maken krijgen met een malafide huiseigenaar, die elk jaar de maximale huurverhoging geeft, maar niets doet aan het onderhoud. Het is natuurlijk makkelijk en goedkoop als een huisbaas opdraait voor reparaties in huis, maar de verhalen over maandenlange lekkages en niet werkende verwarmingen zijn veelgehoord.

    Snel verhuizen
    Als u vaak van baan verwisselt of nog niet precies weet in wat voor woning u wilt wonen is huren vaak de beste optie. U heeft maar een korte opzegtermijn en u kunt zo vertrekken zonder dat u zich zorgen hoeft te maken over de verkoop van een woning.
    Onderhoud van uw woning
    Als u een woning huurt zijn de kosten voor het grote onderhoud aan de woning voor de verhuurder. Bij een eigen woning is dit onderhoud voor uw eigen rekening en zult u zeker eens in de 2 jaar bijvoorbeeld het buitenschilderwerk moeten verzorgen. Uiteraard kunt u dit ook uitbesteden wat natuurlijk ook weer kosten met zich zal meebrengen
    Verbouwen
    Aan een eigen woning mag u zoveel verbouwen als u maar wilt, soms zijn daar zelfs nog subsidies aan verbonden. Uiteraard gelden er wel beperkingen en zal u in sommige gevallen een vergunning aan moeten vragen. Als huurder heb je hierin minder vrijheid en zul je je aan de regels van de verhuurder moeten houden.
    Vaste en variabele kosten
    Bij het huren van een woning heeft u altijd te maken met vaste kosten (afgezien van het percentage huurverhoging per jaar). Bij het kopen van een woning en zeker bij het afsluiten van de hypotheek kunnen de kosten flink variëren, zeker wanneer de rente maar voor een paar jaar is vastgezet.
    huursubsidie
    Bent u een huurder en heeft u te maken met een laag of forse daling van uw inkomen dan kunt u kan huursubsidie aanvragen. huursubsidie is er in principe alleen voor zelfstandige woningen. Dat wil zeggen: woonruimte waarbij u een eigen ingang, badkamer, toilet en keuken hebt. Als u op kamers woont, hebt u geen recht op huursubsidie.
    Woonlasten
    Als huiseigenaar krijgt u te maken met diverse kosten. Vaak zijn het kosten die regelmatig terugkeren: maandelijks, per kwartaal of jaarlijks.
"""

doc_ww = """
    Uit onderzoek van The Royal Society for Public Health (RSPH) blijkt dat mensen die met de auto of met het openbaar vervoer naar werk gaan, serieus schade kunnen oplopen. Het RSPH deed onderzoek naar het reisgedrag van 24 miljoen forenzen in Engeland en Wales, de zogeheten 'passieve' reizigers. Deze forenzen zijn meer gestrest dan fietsers en zijn eerder geneigd om ongezond te eten.

    Wie met de auto naar werk gaat, kent de nadelen. Lange files, asociale weggebruikers en slechte weersomstandigheden maken de rit er niet veel beter op. Wie de trein of de bus pakt, kampt met vertragingen en overvolle voertuigen. Al deze frustraties dragen niet bij aan een goede gezondheid.

    767 CALORIEËN EXTRA

    Volgens het onderzoek geeft 38 procent van de forenzen van deze groep aan hierdoor minder tijd te hebben om thuis ontbijt of lunch te maken en daardoor eerder geneigd zijn iets onderweg te kopen. Dat leidt in de meeste gevallen tot ongezonde snacks. Zelf schatten ze in dat ze daardoor per week zo'n 767 calorieën extra naar binnen werken.

    Natuurlijk is het passief zitten in een auto, trein of bus ook niet bevorderlijk voor de dagelijkse lichamelijke beweging. De groep forenzen geeft aan dat door een lange reistijd minder tijd te hebben om te sporten of gezond te koken, wat leidt tot een hoger BMI en bloeddruk.

    HALTE EERDER UITSTAPPEN

    Wie gezond wil reizen, doet er volgens onderzoeker Roshini Rajapaksa verstandig aan om een halte eerder uit te stappen en te lopen. („Wandelen is een goede manier om te bewegen. Als je met de auto bent, parkeer deze dan verder dan je normaal zou doen.” Ook zou de gestreste forens baat hebben bij ontspannende muziek tijdens frustrerende situaties.

    Daarnaast is het belangrijk gezond te eten en zoveel mogelijk zelf te prepareren. Wie onderweg eet, neigt toch voor de ongezondere optie te gaan. Weinig tijd? Maak dan de avond van tevoren ontbijt, zoals overnight oats. Ook kun je op zondagmiddag alvast voorkoken en porties invriezen.
"""

doc_ww2 = """
    Wanneer is Reistijd ook Werktijd?

    Reistijden voor het woon-werkverkeer beschouwt de wet niet als arbeidstijd. Dat betekent dat uw werknemer de tijd die hij of zij nodig heeft om op het werk te komen of van het werk naar huis te komen niet mag beschouwen als werktijd. Hierover bent u als werkgever dan ook geen reistijdvergoeding verschuldigd. Dat geldt ook voor de soms lange tijd die noodgedwongen moet worden doorgebracht in de file. Ook hiervoor hoeft u als werkgever geen reistijdvergoeding te betalen.

    De Arbeidstijdenwet (Atw)
    De Atw legt de regels vast voor de arbeids- en rusttijden van uw werknemers. De Atw kent een standaardregeling en een overlegregeling. De standaardregeling geldt in principe voor elke werknemer. Zo mag volgens de standaardregeling een werkdag maximaal negen uur duren. In het Arbeidstijdenbesluit staan voor bepaalde groepen personen (zoals chauffeurs) uitzonderingen en aanvullingen op deze regels.
    In de overlegregeling staan iets ruimere normen. Zo mag volgens de overlegregeling een werkdag maximaal tien uur duren. De ruimere normen van de overlegregeling kunnen alleen na overleg met en toestemming van de vakbonden of personeelsvertegenwoordiging worden toegepast. Bijv. zoals in een CAO.

    Reis- of werktijd?
    Moet u de reistijd nu optellen bij de werktijd van uw werknemer? De Atw is daar onduidelijk over. De arbeidsinspectie stelt dat reistijd als werktijd moet worden aangemerkt, als de reis onder gezag van de werkgever is volbracht. Dus wanneer u zich als werkgever kunt bemoeien met de manier waarop en hoe wordt gereisd. Zo kan de chauffeur, die verschillende collega's in een bedrijfsbusje moet ophalen alvorens naar de klant te rijden, zijn reistijd als arbeidstijd tellen.

    De Arbeidsinspectie let in principe op twee dingen; 'hetzelfde karwei' en 'het gezag van de werknemer'. Als een karweiwerker regelmatig naar hetzelfde karwei gaat, telt de reistijd niet als arbeidstijd.

    Woon-werk verkeer
    Volgens de arbeidsinspectie vindt woon-werkverkeer niet onder gezag van u als werkgever plaats. Als uw werknemer dus acht uur per dag moet werken en drie uur per dag moet reizen voor zijn werk, dan bedraagt de arbeidstijd acht uur. De arbeidstijden van de Atw worden dan niet overschreden. Bedraagt de werktijd acht uren en heeft uw werknemer echter onderweg naar verschillende klanten nog drie uur in de file gestaan, dan is de totale werktijd 11 uur en overschrijdt u als werkgever de grenzen van de Atw.

    Werk-werk verkeer
    De arbeidsinspectie beschouwt als werk-werkverkeer de reizen vanaf uw bedrijf naar een project en de reizen van project naar project. Als uw werknemer vanaf thuis voor langere tijd naar hetzelfde project rijdt, dan beschouwt de arbeidsinspectie dit niet als werktijd, tenzij u zich bemoeit met de wijze waarop men reist. Reizen vanaf thuis naar een klant of een project wordt als arbeidstijd beschouwd als het van dag tot dag verschilt en uw werknemer vanaf huis naar verschillende afspraken op een dag rijdt.

    Reistijd, arbeidstijd en beloning
    Als de reistijd arbeidstijd is, ligt het voor de hand dat er een beloning tegenover staat. In de detachering wordt vaak afgesproken dat de reistijd naar de klant aan een maximum is gebonden. Gaat men daar overheen dan wordt de meerdere reistijd als arbeidstijd geteld en vergoed via een reistijdvergoeding. De beloning van reistijd wordt in de CAO geregeld. Per CAO kunnen hierover verschillende afspraken worden gemaakt. Controleer dit dus voor de CAO waaronder u valt. Als uw bedrijf niet onder een CAO valt of de CAO waaronder uw bedrijf valt niets bepaalt, is het raadzaam schriftelijke afspraken met uw personeel te maken over de status van bepaalde reistijden. De arbeidsinspectie kijkt immers bij onenigheid tussen u en uw werknemer eerst wat er op ondernemingsniveau is vastgelegd.



    Meer weten?
    Wilt u meer weten over dit onderwerp en gebruik maken van de vele handige tools en documenten op het gebied van HRM? Klik dan hier voor informatie over HRM-Tools voor leidinggevenden.

    HRM-Tools voor Leidinggevenden
    Heeft u behoefte aan handige tools voor Leidinggevenden? Bijvoorbeeld een tool om zelf arbeidscontracten te kunnen maken. Of voorbeeldmodellen en -teksten die leidinggevenden regelmatig nodig hebben? Inclusief gratis gebruik van onze Digitale Vragenservice voor al uw arbeidsrechtelijke vragen?

    Meld u zich dan aan als gebruiker van de portal HRM-Tools voor Leidinggevenden
"""

dd = [
    doc_onderwijs,
    doc_dh,
    doc_3,
    doc_4,
    doc_shop,
    doc_verhuizing,
    doc_vh_2,
    doc_vh_3,
    doc_ww,
    doc_ww2
]

expected = ['onderwijs', 'detailhandel', 'detailhandel', 'detailhandel', 'winkelen', 'verhuizingen', 'verhuizingen', 'verhuizingen', 'woonwerkverkeer', 'woonwerkverkeer']

print('*************')
print('expected:')
print(expected)
print('*************')
print('result:')
start = time.time()
pp = mm.predict(dd)
print(time.time() - start)
print(pp)
print('*************')
print('Probabilities:')
print('*************')
print(mm.clf.classes_)
start = time.time()
print(mm.clf.predict_proba(dd))
print(time.time() - start)
# print(len(mm.clf.named_steps['tfidf_vect'].vocabulary_))
print(mm.clf.score(dd, expected))

print(metrics.classification_report(expected, pp, target_names = ['detailhandel','onderwijs','ww']))

print('*************')
print('*************')
print('~~~~~~~~~~~~~')
print('~~~~ MNB ~~~~')
print('~~~~~~~~~~~~~')
print('*************')
print('*************')


print('*************')
print('expected:')
print(expected)
print('*************')
print('result:')
pp = mm.mnb.predict(dd)
print(pp)
print('*************')
print('Probabilities:')
print('*************')
print(mm.mnb.predict_proba(dd))
print(mm.mnb.score(dd, expected))

print(metrics.classification_report(expected, pp, target_names = ['detailhandel','onderwijs','ww']))
