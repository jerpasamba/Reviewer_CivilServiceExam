import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HTML = r'D:\VS_Code_Repositories\CiviilServiceReviewer\quiz.html'

# n: (question, [o1, o2, o3, o4], answer_index)
MATH = {
    1: ("If 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 = 55, then 11 + 12 + 13 + 14 + 15 + 16 + 17 + 18 + 19 + 20 = ?", ["65", "155", "125", "550"], 1),
    2: ("Evaluate: {16 – (24 – 8) + 22 × 8 – 8}.", ["40", "48", "64", "168"], 3),
    3: ("Find the product: 800 × 125.", ["925", "1000", "10 000", "100 000"], 3),
    4: ("Find the quotient: 8 000 ÷ 125", ["48", "64", "80", "88"], 1),
    5: ("Find the sum: 299 + 943 + 398 + 101", ["1,531", "1,641", "1,741", "122,222"], 2),
    6: ("If 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10 = 55, then 101 + 102 + 103 + 104 + 105 + 106 + 107 + 108 + 109 + 110 = ?", ["1,055", "1,065", "1,075", "5,500"], 0),
    7: ("What is the remainder when 192 888 is divided by 8?", ["0", "4", "8", "24"], 0),
    8: ("Rounding 299 943 to the nearest thousands, the result is", ["299 940", "299 000", "299 900", "300 000"], 3),
    9: ("If 23 + 28 + 37 + x + 53 = 168 and 23 + 28 + 40 + y + 50 = 120. Find the value of x – y?", ["36", "48", "56", "64"], 1),
    10: ("398.101 is read as", ["three hundred ninety eight, one hundred one.", "three hundred ninety eight and one hundred one.", "three hundred ninety eight and one hundred one hundredths", "three hundred ninety eight and one hundred one thousands"], 3),
    11: ("A number is divisible by 8 if its last three digits is divisible by 8. Which of the following numbers is divisible by 8?", ["9 208", "6 236", "88 254", "8 886"], 0),
    12: ("Which of the following statements is true?", ["If a number is divisible by 5, then it is divisible by 10.", "If a number is divisible by 10, then it is divisible by 5.", "If a number is divisible by 3, then it is divisible by 6.", "If a number is divisible by 4, then it is divisible by 8."], 1),
    13: ("Simplify: ½ (128 – 84) + (128 – 84) – ½ (128 – 84)", ["0", "20", "44", "64"], 2),
    14: ("Simplify: 33 1/3% of 48 + 12 ½% of 96 – 44 4/9% of 27", ["12", "16", "24", "48"], 1),
    15: ("Reduce 231/1001 to its lowest terms", ["7/11", "3/31", "3/13", "7/13"], 2),
    16: ("Which of the following is true?", ["-16 > 8", "8/64 = ¼", "54 – 8 ≥ 8 – 54", "9/117 = 1/17"], 2),
    17: ("Find the value of x: (3/8)(72) + (5/7)(35)", ["27", "36", "45", "52"], 3),
    18: ("What is 25% of 228?", ["52", "57", "54", "912"], 1),
    19: ("228 is 25% of what number?", ["52", "57", "54", "912"], 3),
    20: ("168 is what percent of 672?", ["25%", "50%", "400%", "80%"], 0),
    21: ("Evaluate: 123 × 0.1 + 123 × 0.01 + 123 × 0.001", ["13.653", "135.53", "1 356.3", "13 563"], 0),
    22: ("Find 3 ¼ of 16", ["7", "16", "39", "52"], 3),
    23: ("Evaluate: 1 + ½ + ¼ + 1/8 = ?", ["1 3/16", "1 3/8", "1 5/8", "1 7/8"], 3),
    24: ("Find the value of x in the equation: 3x + 7 = 28", ["7", "-7", "±7", "4"], 0),
    26: ("Which of the following cannot yield an odd integer when divided by 10?", ["The sum of two odd integers.", "The product of a prime number and an odd integer", "The product of two odd integers", "The sum of three consecutive integers"], 2),
    27: ("If 8x + 12 = 24, what is the value of 24x + 36", ["4", "6", "8", "72"], 3),
    28: ("If a positive integer m is divisible by both 3 and 8, then m must also be divisible by", ["10", "18", "24", "60"], 2),
    29: ("If positive integers m and n are not both odd, which of the following is always true?", ["m + n is even", "mn is even", "m – n cannot be odd", "m + n – 1 is odd"], 1),
    30: ("Find the average temperature change for the 12-day period. Temperature change in degree celsius: 2.6, 3.8, 7.0, 4.5, 4.6, 7.9, 5.0, 8.1, 4.4, 5.3, 6.4, 5.2", ["4.8", "4.9", "5.2", "5.4"], 3),
    31: ("Find the set of all odd numbers x satisfying the conditions 5x - 4 ≤ 0 and 3x – 7 ≥ 0", ["{x | x ≠ 1}", "{1}", "{x | x ∈ ∅}", "{∅}"], 3),
    32: ("State the property illustrated. If 8(6) + 4 = 48 + 4 = 52, then 8(6) + 4 = 52", ["distributive property of multiplication over addition", "commutative property of addition", "associative property", "transitive property of equality"], 3),
    33: ("If 8 less than the product of a number and -3 is greater than 7, which of the following could be that number?", ["-6", "-5", "5", "6"], 0),
    34: ("The difference between 8 times a number and 17 is 231. Find the number.", ["31", "37", "48", "1 984"], 0),
    35: ("Four times the perimeter of a parking lot is 16 less than 2,000 meters. What is the perimeter of the lot?", ["496 m", "504 m", "992 m", "1,008 m"], 0),
    36: ("The amount of last month’s telephone bill, decreased by the product of 3 and Php30.00 equals Php1,319.50. Find the amount of last month’s telephone bill.", ["Php 1,229.50", "Php 1,289.50", "Php 1,310.50", "Php 1,409.50"], 3),
    37: ("Eighteen less than seven times the number of sandwiches is 269. How many sandwiches are there?", ["32", "41", "44", "45"], 1),
    38: ("A house and lot are sold for Php 14M. The house costs 1.5 times as much as the lot. How much does the lot cost?", ["Php 5.6M", "Php 8.4M", "Php 10.5 M", "Php 21M"], 0),
    39: ("The sale price of a television set is Php 7,200. The discount rate is 40%. Find its regular price.", ["Php 4,320", "Php 12,000", "Php 6,800", "Php 10,000"], 1),
    40: ("The lengths of the sides of a triangle can be represented by three consecutive integers. The perimeter of the triangle is 96cm. Find the length of the longest side of the triangle.", ["28", "32", "33", "36"], 2),
    41: ("The length of a rectangle is 8 meters more than twice its width. The perimeter is 112 meters. Find its area.", ["16m²", "24m²", "28 m²", "640 m²"], 3),
    42: ("Paula is twice as old as Queenie. Seven years ago the sum of their ages was 16. How old is Queenie now?", ["8", "10", "16", "20"], 1),
    43: ("For what value of x will x be the average of 2, 4x, 6, 8, 10?", ["4", "12", "26", "39"], 2),
    44: ("How many integers between 197 and 303 are divisible by 4 or 10?", ["25", "26", "31", "37"], 2),
    45: ("A patient must take his medication every 7 hours starting at 7:00 AM, Sunday. On what day will the patient first receive his medication at 8 AM?", ["Sunday", "Wednesday", "Thursday", "Tuesday"], 3),
    46: ("Of the 300 grocery shoppers surveyed, 96 did not have a regular day of the week on which they shop. What percentage of the shoppers did not have a regular day of shopping?", ["32%", "48%", "64%", "96%"], 0),
    47: ("A water container has 100mL of water in it and is 20% full. How many mL of water can this container hold if it is full?", ["200 mL", "400 mL", "500 mL", "800 mL"], 2),
    48: ("How many containers each occupies an area of 2 1/8 square meters can be stored in a 952 square meter warehouse?", ["358", "448", "530", "630"], 1),
    49: ("A starting salary of a secretary at ABC Computer Specialists is Php15,000 a month. Next year the starting salary will be raised to Php18,000. What is the rate of increase in the starting salary?", ["3%", "20%", "25%", "30%"], 1),
    50: ("The cost of a square meter commercial lot in a certain municipality five years ago was Php12,500. There was a 420% increase in the price in the last five years. What is the price per square meter of that lot today?", ["Php 17,500", "Php 52,500", "Php 19,000", "Php 65,000"], 3),
    51: ("Last month, a store manager decided to decrease the prices of all items by 10%. This month, he increased the prices by 10%. What would be the price for a pair of pants that had cost Php750 before prices were decreased last month?", ["Php 742.50", "Php 750.00", "Php 675.00", "Php 825.00"], 0),
    52: ("When the original price of an item is increased by a certain rate, the increased price is Php 3,100. When the original price is decreased by the same rate, the decreased price is Php1,900. What is the original price of this item?", ["Php 1,200", "Php 200", "Php 2,500", "Php 2,800"], 2),
    53: ("How much must one has to invest in corporate bonds paying 9.6% in order to earn an income of Php12,000 per annum?", ["Php 11,520", "Php 23,040", "Php 125,000", "Php 250,000"], 2),
    54: ("How much must be cut from the edge of a piece of glass 16 1/8 cm wide, in order for it to fit into an opening 14 ¾ cm wide?", ["2 3/8cm", "1 7/8cm", "1 3/8cm", "2 5/8 cm"], 2),
    55: ("A race car traveled for 2 ½ hours with an average speed of 132 5/8 km per hour. Find the total distance it covered.", ["264 5/16km", "331 9/16km", "330 5/16km", "135 1/8km"], 1),
    56: ("If the weight of a 241-kg freight car increases 3 1/8 times when fully loaded, what will be its weight with a full load?", ["750 3/8kg", "824 3/8kg", "720 5/8kg", "753 1/8kg"], 3),
    57: ("How many liters will remain in a 1,000-liter storage tank if 8.2% of the liquid has evaporated due to excessive heat?", ["918", "991.8", "999.18", "998"], 0),
    58: ("Dante recently sold some stocks for which he originally bought for Php358. If it has increased in value by 116%, how much did he receive for the stock?", ["Php678.27", "Php772", "Php773.28", "Php778"], 2),
    59: ("Mr. Manny Vargas, a real estate broker sold a building for Php175M. How much did he receive if his commission is 5.5% of the sale price of the property?", ["Php9.5M", "Php9.7M", "Php9.625M", "Php180.5M"], 2),
    60: ("If 560 out of 700 examinees passed in the recent Career Service exam for SubProfessional level, what percent of the examinees passed?", ["65%", "72%", "80%", "140%"], 2),
    61: ("Mr. Cruz borrows Php750,000 from Asian Bank and is charged Php90,000 interest. What rate of interest did Asian Bank charge for the loan?", ["8%", "9%", "10%", "12%"], 3),
    62: ("A store sells shirts for Php1,078 each or 3 for Php2,997. How much would one save by buying 3 shirts at a time instead of 3 shirts, one at a time?", ["237", "921", "1,237", "1,921"], 0),
    63: ("A computer can be rented for Php1,745 a week or Php 347.50 a day. You need the computer only for 6 days. At which rate (daily or weekly), would it be cheaper to rent and by how much cheaper?", ["weekly: Php340", "daily: Php240", "daily: Php340", "weekly: Php240"], 0),
    64: ("A 1.25 kg of box of Brand A detergent sells for Php 87.50. A 1.5 kg box of Brand B detergent sells for Php103.20. What is the difference in the price per kg?", ["Php 1.20", "Php 1.50", "Php 1.80", "Php 2.00"], 0),
    65: ("A 30-cm long plastic pipe costs Php249. At this rate, what is the price of the pipe per meter?", ["Php 830", "Php 840", "Php 747", "Php 749"], 0),
    66: ("A homeowner can rent a chain saw from a rental agency at Php 2,700 a day. The brand new of the same saw can be bought for Php18,900. For how many days could the homeowner rent the saw before renting would cost more than buying?", ["5", "6", "7", "8"], 2),
    67: ("Paula uses ten 100-watt bulbs in her house. She uses these bulbs at an average of 5 hours each day. How many KWH do these bulbs use each day?", ["5", "10", "50", "5,000"], 0),
    68: ("An electric range uses 12,200 watts per hour and is run an average of 60 hours a year. How many kilowatt-hour is this?", ["73.2", "732", "7,320", "7.32"], 1),
    69: ("A DVD movie, purchased for Php440 was marked up 25% on the selling price. Later, as retail prices fell, this movie was marked down 20% on the current sale price. Find its new sale price.", ["Php 352", "Php 440", "Php 500", "Php 550"], 1),
    70: ("VNS Inc. bought these office supplies last week: 1,320 pens @ Php 0.125; 1,480 packs paper clips @ Php 0.625; 1,240 boxes of tape @ Php 0.875; 1,720 boxes of cards @ 0.80. A 5% sales tax is added. What was the company’s total bill?", ["Php 173.25", "Php 3,551", "Php 971.25", "Php 3,728.55"], 3),
    71: ("The question “How many flowers are needed to border a rectangular garden?”, involves", ["weight", "perimeter", "volume", "area"], 1),
    72: ("How many meters of fencing are needed to enclose an 84-meter by 48-meter rectangular garden?", ["132m", "244m", "264m", "4,032m2"], 2),
    73: ("How many 1-cm square stickers are needed to cover a photo box 4 cm long, 3cm wide and 5cm high?", ["47", "60", "88", "94"], 3),
    74: ("One side of a triangle is 3cm longer than the shortest side, and the other side is 4cm longer than the shortest side. How long is the shortest side if the perimeter is 67 cm?", ["20 cm", "23 cm", "24 cm", "27 cm"], 0),
    75: ("The length of a rectangle is 2cm less than twice its width. What is its width in cm, if its perimeter is 50cm?", ["8", "9", "16", "25"], 1),
}

# n: (section, new_options, new_answer)
FIX_OPTS = {
    ("inductive_reasoning", 30): (["318", "314", "316", "312"], None),
    ("inductive_reasoning", 50): (["e3e2", "e4e4", "e2e2", "e3e3"], 3),
    ("alphabetizing", 5): (["CBAD", "CDAB", "CABD", "CADB"], None),
}

html = open(HTML, encoding='utf-8').read()
m = re.search(r'const DATA = (.*);\r?\nconst GROUPS', html, re.S)
data = json.loads(m.group(1))

applied = []
for q in data['math_word_problems']:
    if q['n'] in MATH:
        nq, no, na = MATH[q['n']]
        old_a = q['a']
        if len(q['o']) != 4 or set(q['o']) != set(no):
            applied.append(('math %s' % q['n'], 'rebuilt (was %s opts)' % (len(q['o']),)))
        elif old_a != na:
            applied.append(('math %s' % q['n'], 'answer %d -> %d' % (old_a, na)))
        q['q'], q['o'], q['a'] = nq, no, na

for (sec, n), (no, na) in FIX_OPTS.items():
    for q in data[sec]:
        if q['n'] == n:
            q['o'] = no
            if na is not None:
                q['a'] = na
            applied.append((sec + ' %s' % n, 'options replaced'))

# readability: add commas to space-separated sequences in inductive_reasoning
pat = re.compile(r'^[\w]+( [\w]+)+$')
for q in data['inductive_reasoning']:
    if pat.match(q['q']) and ',' not in q['q']:
        q['q'] = ', '.join(q['q'].split())
        applied.append(('inductive_reasoning %s' % q['n'], 'commas added'))

new = json.dumps(data, ensure_ascii=False, separators=(', ', ': '))
html2 = html[:m.start(1)] + new + html[m.end(1):]
open(HTML, 'w', encoding='utf-8', newline='').write(html2)

print('Applied %d fixes:' % len(applied))
for a in applied:
    print('  ', a)
print('math section n present:', sorted(q['n'] for q in data['math_word_problems']))
