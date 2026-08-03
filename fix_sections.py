# Fix structurally degraded sections in quiz.html:
#   identifying_errors  -> mark sentence parts with [A]..[D] (error sits in the part
#                          matching the answer key letter; E = no error)
#   paragraph_development-> attach the A-F passage sentences to each question
#   correct_usage       -> restore the missing blank (___) and repair corrupt options
#   antonyms            -> repair the two single-option questions (n=18, n=38)
import io, json, re

SRC = r"D:\VS_Code_Repositories\CiviilServiceReviewer\quiz.html"
html = io.open(SRC, encoding="utf-8").read()

i = html.find("const DATA = ")
start = html.find("{", i)
depth = 0
for k in range(start, len(html)):
    if html[k] == "{":
        depth += 1
    elif html[k] == "}":
        depth -= 1
        if depth == 0:
            end = k + 1
            break
data = json.loads(html[start:end])

# ---------------- Identifying Errors ----------------
IE = {
1: "[A]No one [B]were [C]happy [D]about the Mindanao crisis.",
2: "[A]The House of Representatives' decision [B]to decrease the budget [C]for the Department of [D]Education was met with protests.",
3: "[A]The Cabinet [B]regularly [C]meet [D]once a week.",
4: "[A]Both [B]the Senators and [C]the Congressmen [D]legislate laws.",
5: "[A]The Philippine government [B]have [C]three branches of powers: [D]the executive, the legislative and the judicial.",
6: "[A]The Supreme Court [B]upholds the highest [C]principles and standards [D]of morality as embodied in the Constitution.",
7: "[A]Some [B]historians [C]contests [D]the origin of the Filipino flag.",
8: "[A]Some believe that the flag [B]we use now is [C]not the same as the one [D]made by Marcela Agoncillo.",
9: "[A]Either Prof. Teodoro Agoncillo or [B]Dr. Gregorio F. Zaide affirm [C]the history [D]of our flag.",
10: "[A]The news [B]are written [C]immediately [D]to meet the previous deadline.",
11: "[A]Attempts [B]is made [C]to locate and restore [D]the last original Filipino flag.",
12: "[A]Both Chelle [B]and Charm [C]enjoys [D]reading.",
13: "[A]Reading books [B]widens [C]one's [D]horizons.",
14: "[A]If everybody [B]know [C]how to read, [D]then books will never cease to be useful.",
15: "[A]No one [B]dares to question [C]how invaluable [D]books are.",
16: "[A]Great literary [B]works [C]enriches [D]the vocabulary of their readers.",
17: "[A]Have [B]either of the books [C]been [D]returned?",
18: "[A]One hundred fifty pesos [B]are [C]the average selling price [D]of one textbook.",
19: "[A]One of the machines [B]in the printing press [C]weren't [D]functioning properly.",
20: "[A]Either [B]the teachers or [C]the librarian, [D]take care of the books.",
21: "[A]A number of [B]books [C]is regularly [D]donated to public schools.",
22: "[A]The number of [B]readers [C]continually [D]rise each year.",
23: "[A]For I, [B]Reader's Digest [C]is informative [D]as well as entertaining.",
24: "[A]The Manila Bulletin [B]has been published [C]the Panorama magazine [D]for over a hundred years.",
25: "[A]All children [B]has [C]inherent rights [D]that must be protected.",
26: "[A]The editor-in-chief, together [B]with the writers, [C]confers about [D]the contents of their newspapers.",
27: "[A]Gorio and Tekla, in addition [B]to Captain Barbel, [C]was [D]a popular comic books during the '70s.",
28: "[A]Pol Medina [B]has drew [C]the very famous [D]Pugad Baboy characters.",
29: "[A]Pugad Baboy [B]first appear [C]in the Philippine [D]Daily Inquirer during the late '80s.",
30: "[A]Neither Pol Medina nor [B]his friends [C]thinks [D]he will become successful.",
31: "[A]Some believes [B]that Mr. Medina's works [C]satirize the socio-economic [D]condition of the people in our country.",
32: "[A]The youth delegates [B]have been [C]sang [D]the National Anthem.",
33: "[A]That house and lot [B]in the corner [C]are [D]government-owned.",
34: "[A]The number of socialized [B]housing units sponsored [C]by the government [D]increases each year.",
35: "[A]A quarter of the [B]government tax [C]collections [D]goes to infrastructure projects.",
36: "[A]The beneficiaries of the [B]study grant given [C]by the government [D]will be them.",
37: "[A]Studies suggests [B]that exposure to [C]too much violence [D]on television makes one equally violent.",
38: "[A]The possible effects [B]of television viewing [C]needs [D]to be explored further.",
39: "[A]Every weekdays, Chel [B]and Charm [C]goes [D]to school together.",
40: "[A]The Scent of Apples, a story [B]about a Filipino who [C]immigrated to the United States are written [D]by Bienvenido Santos.",
41: "[A]Nick Joaquin, one of the [B]exceptional Filipino writers, [C]is also known [D]for Quijano de Manila.",
42: "[A]Some people [B]believes [C]that one could see [D]his future mate by looking into a mirror on May day eve.",
43: "[A]Jose Garcia Villa [B]was a recipient of [C]numerous awards, [D]between them, the 'National Artist Award for Literature'.",
44: "[A]The Far Eastern University [B](FEU) also gave he [C]a Doctor of Literature [D]honoris causa in 1959, aside from asking him to be a visiting professor.",
45: "[A]Between [B]the numerous prose [C]writers, I think [D]Nick Joaquin is the best.",
46: "[A]Those [B]are [C]work [D]of famous authors.",
47: "[A]The professor asked [B]her a question [C]about [D]they.",
48: "[A]Literature seem [B]elusive to people [C]who profess [D]indifference to it.",
49: "[A]It appeals [B]both to the [C]readers intellect [D]and passion.",
50: "[A]Robert Frost, an American poet, [B]defines litereature [C]as 'performance [D]in words.'",
51: "[A]Either of [B]the authors [C]have received [D]citations for their remarkable works.",
52: "[A]Just like Edgar Allan Poe, [B]it is believed that Nick Joaquin [C]starts getting ideas after [D]he has drank alcoholic beverages.",
53: "[A]Computers are [B]widely [C]use [D]nowadays even in preschools.",
54: "[A]The number of Computer [B]Science students [C]steadily [D]increases.",
55: "[A]AMA, in addition to STI, train [B]students to be [C]proficient in [D]computer use.",
56: "[A]Knowledge should [B]always be put [C]to good [D]use.",
57: "[A]One of the viruses [B]has infect [C]my brother's brand [D]new laptop computer.",
58: "[A]Internet access [B]allow us [C]to communicate with [D]other people anywhere in the world.",
59: "[A]All of the [B]pens [C]are no spent [D]yesterday.",
60: "[A]Each computer [B]come with [C]either a compact [D]disk player or a DVD player.",
}
for q in data["identifying_errors"]:
    q["q"] = IE[q["n"]]

# ---------------- Paragraph Development ----------------
PI = ("A. The first procedure is that the bill passes through three readings on separate days.\n"
      "B. Otherwise, the bill will go back to the House from where it originated, and it will be deliberated upon again.\n"
      "C. If the President approves the bill, then it shall be deemed a law.\n"
      "D. A bill, before becoming a law, undergoes several procedures.\n"
      "E. On the third reading, the votes of the lawmakers shall be recorded and if the bill is approved, it goes to the President for approval or veto.")
PII = ("A. Learning to listen is one way of keeping friends.\n"
       "B. Although listening can really be very tiring on the listener, it may, on the other hand, be comforting to the speaker.\n"
       "C. So learn how to listen, and gain more friends.\n"
       "D. We also show that we care about what goes on in their lives.\n"
       "E. By listening, we show our friends that they are important to us.")
PIII = ("A. Hence, it can be said that the President really has a lot of duties and responsibilities.\n"
        "B. He has control over department secretaries and can overrule their decisions.\n"
        "C. Furthermore, the President exercises veto power over bills passed by the Congress.\n"
        "D. Lastly, he is the Chief Executive, executing the laws and rules of the country.\n"
        "E. The president in a presidential system is the Head of the State and the Head of Government.")
PIV = ("A. Not only that, paying taxes also means the government will no longer need to acquire loans to fill the budget deficit.\n"
       "B. Every citizen should lend a hand in pursuing economic progress.\n"
       "C. One way to do it is to pay one's taxes correctly.\n"
       "D. Paying correct taxes results in increased revenues that the government uses for infrastructure and other projects.\n"
       "E. So be a good citizen and pay your taxes correctly.")
FS = ("F. It should be noted, however, that the President must communicate his veto within thirty days from receipt of the bill, "
      "otherwise, the bill is considered to have been approved by him.")
PD_PASS = {
    1: PI, 2: PI, 3: PI + "\n\n" + FS, 4: PII, 5: PII,
    6: PIII, 7: PIII, 8: PIV, 9: PIV, 10: PIV,
}
for q in data["paragraph_development"]:
    q["p"] = PD_PASS[q["n"]]
    if q["n"] == 2:
        q["o"] = ["A", "B", "C", "D", "E"]

# ---------------- Correct Usage ----------------
CU = {
1: "Lily ___ remarkable poems even at her young age.",
2: "Being too ___ will undoubtedly make other men hate you.",
3: "Due to bad weather, the airline company decided ___ postpone the flight.",
4: "Drunk driving was the reason for ___ accident.",
5: "May I ___ your Titanic compact disk?",
6: "___ the three girls, the eldest is the most diligent.",
7: "Exposure to air pollution will ___ your asthma.",
8: "His ___ to Mount Apo was carefully documented.",
9: "The children ___ the ill effects of war.",
10: "The teachers distributed different ___ outlines for the students to follow.",
11: "Carl juggles oranges, ___ you?",
12: "The refugees decided to ___ their homes because of the war.",
13: "My sister ___ to Zamboanga seven years ago.",
14: "We used ___ sauce for the spaghetti last Sunday.",
15: "If we work together, we could finish this ___ in a short time.",
16: "When the Apartheid Policy was still in effect, the Blacks were ___ by the Whites?",
17: "When we ___ the flag, we should all stand up.",
18: "The DPWH crew worked ___ the night to repair the damaged bridge.",
19: "___ the leader of your group?",
20: "The village elder told many interesting ___.",
21: "Marty ___ Evelyn ___ to dinner.",
22: "The celebrant ___ candles after we sang.",
23: "The secretary ___ due to stress.",
24: "The Edsa People's Revolution ___ the Marcos regime.",
25: "The unexpected ___ of vehicles along Marcos Highway caused heavy traffic.",
26: "After cleaning the entire house, I felt ___.",
27: "The drug pushers tried to ___ the arresting cops.",
28: "The Cabinet meeting was ___ on account of the President's ill health.",
29: "The tele-novela viewers cried helplessly when they got ___ by the tragedy that befell the main character.",
30: "We should ___ on our expenditures and spend only on our needs.",
31: "People of all races should try to ___ with each other.",
32: "We should grow wiser as time ___.",
33: "The partying teens were told to ___ the noise.",
34: "A gust of strong wind ___ the old wooden swing.",
35: "A number of factory workers were ___ due to retrenchment.",
36: "We should never ___ people with disabilities for they also have the right to live.",
37: "Stop ___ your younger brother so he will stop crying.",
38: "Always ___ your best effort in everything you do.",
39: "Did you help in ___ the table?",
40: "She ___ the details of the program.",
}
CU_OPTS = {
    4: ["their", "they're", "there", "there are"],
    5: ["borrow", "lend", "loan", "credit"],
    18: ["three", "through", "trough", "true"],
    38: ["put across", "put down", "put forth", "put out"],
    39: ["setting apart", "setting back", "setting down", "setting up"],
}
for q in data["correct_usage"]:
    q["q"] = CU[q["n"]]
    if q["n"] in CU_OPTS:
        q["o"] = CU_OPTS[q["n"]]

# ---------------- Antonyms ----------------
for q in data["antonyms"]:
    if q["n"] == 18:
        q["q"] = "Heinous criminals are truly loathsome."
        q["o"] = ["repugnant", "foul", "adorable", "nasty"]
        q["a"] = 2
    elif q["n"] == 38:
        q["q"] = "That yonder youth is more studious than the nearer one."
        q["o"] = ["lonesome", "farther", "closer", "thither"]
        q["a"] = 2

out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
html = html[:start] + out + html[end:]
io.open(SRC, "w", encoding="utf-8").write(html)
print("fixes applied; sections now:")
for sec in ("identifying_errors", "paragraph_development", "correct_usage", "antonyms"):
    print(" ", sec, len(data[sec]))
