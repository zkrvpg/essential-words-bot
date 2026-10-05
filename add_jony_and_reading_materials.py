"""
Populates Reading for the Real World (Books 7-10) and IELTS Core Vocabulary (Book 11)
into essential_words.db to expand vocabulary alongside 4000 Essential English Words.
"""
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "essential_words.db"

# Reading for the Real World 1-4 & IELTS data
NEW_BOOKS = [
    {
        "id": 7,
        "title": "Reading for the Real World 1",
        "cefr_level": "B1",
        "description": "Akademik o'qish va yangi ilmiy so'zlar (Compass Publishing, B1)",
        "units": [
            {
                "unit_number": 1,
                "title": "Strange & Unusual (Sirli va G'aroyib)",
                "story": "Throughout history, there have been countless unexplained phenomena that captivate human imagination. From reports of sea monsters like the Loch Ness monster to sightings of unidentified flying objects (UFOs), people are fascinated by the mysterious. While skeptics search for rational explanations, enthusiasts continue to seek definitive proof that these strange creatures and events genuinely exist.",
                "words": [
                    ("phenomenon", "/fəˈnɒmɪnən/", "n.", "ot (noun)", "A remarkable or unexplained event.", "Volcanic eruptions are a powerful natural phenomenon.", "hodisa, ajoyib voqea"),
                    ("captivate", "/ˈkæptɪveɪt/", "v.", "fe'l (verb)", "To attract and hold someone's interest.", "The mysterious story captivated the audience.", "o'ziga jalb qilmoq"),
                    ("unidentified", "/ˌʌnaɪˈdentɪfaɪd/", "adj.", "sifat (adjective)", "Not recognized or proven.", "They reported seeing an unidentified flying object.", "noma'lum, aniqlanmagan"),
                    ("skeptic", "/ˈskeptɪk/", "n.", "ot (noun)", "A person who doubts common beliefs.", "Skeptics demanded proof before believing the claim.", "shubhalanuvchi, skeptik"),
                    ("rational", "/ˈræʃənl/", "adj.", "sifat (adjective)", "Based on reason or logic.", "Scientists look for rational explanations for events.", "mantiqiy, aqlga to'g'ri"),
                    ("definitive", "/dɪˈfɪnətɪv/", "adj.", "sifat (adjective)", "Final, unquestionable, and conclusive.", "There is still no definitive proof of life on Mars.", "aniq, so'nggi, qat'iy"),
                    ("enthusiast", "/ɪnˈθjuːziæst/", "n.", "ot (noun)", "A person who is highly interested in a topic.", "Aviation enthusiasts gathered for the airshow.", "ishqiboz, qiziquvchi"),
                    ("genuinely", "/ˈdʒenjuɪnli/", "adv.", "ravish (adverb)", "Truly or sincerely.", "He was genuinely surprised by the strange discovery.", "haqiqatan ham, chindan"),
                    ("bizarre", "/bɪˈzɑːr/", "adj.", "sifat (adjective)", "Extremely strange or unusual.", "The strange painting depicted bizarre creatures.", "g'alati, beo'xshov"),
                    ("mythical", "/ˈmɪθɪkl/", "adj.", "sifat (adjective)", "Existing only in myths or legends.", "Dragons and unicorns are mythical beasts.", "afsonaviy, to'qima"),
                    ("witness", "/ˈwɪtnəs/", "n.", "ot (noun)", "A person who sees an event take place.", "The witness testified that she saw bright lights.", "guvoh"),
                    ("speculate", "/ˈspekjuleɪt/", "v.", "fe'l (verb)", "To form theories without firm evidence.", "Experts speculate about the origins of the artifact.", "taxmin qilmoq"),
                    ("illusion", "/ɪˈluːʒn/", "n.", "ot (noun)", "A deceptive appearance or false impression.", "Mirages in the desert create the illusion of water.", "illyuziya, xomxayol"),
                    ("investigate", "/ɪnˈvestɪɡeɪt/", "v.", "fe'l (verb)", "To examine or research thoroughly.", "Detectives were called to investigate the crime.", "tekshirmoq, surishtirmoq"),
                    ("convince", "/kənˈvɪns/", "v.", "fe'l (verb)", "To cause someone to believe firmly.", "Strong evidence convinced the jury of his innocence.", "ishontirmoq")
                ]
            },
            {
                "unit_number": 2,
                "title": "Computers & Technology (Kompyuter va Texnologiya)",
                "story": "Modern technological breakthroughs have fundamentally transformed how humans communicate, work, and learn. Artificial intelligence and automation have begun replacing repetitive human labor, raising profound ethical questions. As technological innovation accelerates, societies must balance productivity gains against the potential disruption to employment and privacy.",
                "words": [
                    ("breakthrough", "/ˈbreɪkθruː/", "n.", "ot (noun)", "A major sudden advance or discovery.", "Scientists achieved a medical breakthrough in cancer research.", "ulkan kashfiyot, burilish"),
                    ("fundamentally", "/ˌfʌndəˈmentəli/", "adv.", "ravish (adverb)", "At the most basic or essential level.", "The internet fundamentally altered global commerce.", "tubdan, asosiy jihatdan"),
                    ("automation", "/ˌɔːtəˈmeɪʃn/", "n.", "ot (noun)", "The use of machines to perform tasks.", "Factory automation increased manufacturing speed.", "avtomatlashtirish"),
                    ("repetitive", "/rɪˈpetətɪv/", "adj.", "sifat (adjective)", "Repeating again and again; monotonous.", "Robots are ideal for performing repetitive tasks.", "takroriy, zerikarli"),
                    ("profound", "/prəˈfaʊnd/", "adj.", "sifat (adjective)", "Very deep, significant, or intense.", "The new discoveries had a profound impact on science.", "chuqur, jiddiy"),
                    ("accelerate", "/əkˈseləreɪt/", "v.", "fe'l (verb)", "To increase in speed or rate.", "Technological progress continues to accelerate.", "tezlashmoq, jadallashmoq"),
                    ("disruption", "/dɪsˈrʌpʃn/", "n.", "ot (noun)", "Disturbance or drastic alteration.", "New software caused temporary disruption to services.", "buzilish, to'xtalish"),
                    ("privacy", "/ˈprɪvəsi/", "n.", "ot (noun)", "The state of being free from unwanted observation.", "Users are increasingly concerned about digital privacy.", "shaxsiy hayot daxlsizligi"),
                    ("artificial", "/ˌɑːtɪˈfɪʃl/", "adj.", "sifat (adjective)", "Made or produced by human beings rather than nature.", "Artificial intelligence assists doctors in diagnosis.", "sun'iy"),
                    ("capacity", "/kəˈpæsəti/", "n.", "ot (noun)", "The maximum amount that can be contained or produced.", "The new hard drive has immense storage capacity.", "sig'im, qobiliyat"),
                    ("efficient", "/ɪˈfɪʃnt/", "adj.", "sifat (adjective)", "Achieving maximum productivity with minimum wasted effort.", "Electric motors are remarkably efficient machines.", "samarali, tejamkor"),
                    ("obsolete", "/ˈɒbsəliːt/", "adj.", "sifat (adjective)", "No longer produced or used; out of date.", "Floppy disks have become completely obsolete.", "eskirgan, urfdan qolgan"),
                    ("integrate", "/ˈɪntɪɡreɪt/", "v.", "fe'l (verb)", "To combine or incorporate into a whole.", "The school decided to integrate technology into classrooms.", "birlashtirmoq, integratsiya qilmoq"),
                    ("virtual", "/ˈvɜːtʃuəl/", "adj.", "sifat (adjective)", "Existing by means of digital software rather than physically.", "Students attended classes in a virtual environment.", "virtual, kompyuterdagi"),
                    ("device", "/dɪˈvaɪs/", "n.", "ot (noun)", "An instrument designed to perform a specific function.", "Smartphones are versatile electronic devices.", "qurilma, asbob")
                ]
            },
            {
                "unit_number": 3,
                "title": "Health & Medicine (Salomatlik va Tibbiyot)",
                "story": "Maintaining good health requires more than just curing illnesses; preventative medicine is vital. Chronic lifestyle diseases such as hypertension and diabetes can often be mitigated by adopting nutritious diets and engaging in consistent physical exercise. Breakthroughs in genetics now enable doctors to customize treatments for individual genetic profiles.",
                "words": [
                    ("preventative", "/prɪˈventətɪv/", "adj.", "sifat (adjective)", "Designed to keep something undesirable from happening.", "Regular check-ups are effective preventative measures.", "profilaktik, oldini oluvchi"),
                    ("chronic", "/ˈkrɒnɪk/", "adj.", "sifat (adjective)", "Persisting for a long time or constantly recurring.", "He suffered from chronic back pain for years.", "surunkali"),
                    ("mitigate", "/ˈmɪtɪɡeɪt/", "v.", "fe'l (verb)", "To make less severe, serious, or painful.", "Drinking water helps mitigate the effects of heat.", "yumshatmoq, yengillashtirmoq"),
                    ("nutritious", "/njuːˈtrɪʃəs/", "adj.", "sifat (adjective)", "Efficient as food; nourishing.", "Fresh fruits and vegetables are highly nutritious.", "to'yimli, foydali"),
                    ("consistent", "/kənˈsɪstənt/", "adj.", "sifat (adjective)", "Unchanging in achievement or steady practice.", "Consistent exercise leads to long-term fitness.", "muntazam, barqaror"),
                    ("customize", "/ˈkʌstəmaɪz/", "v.", "fe'l (verb)", "To modify according to individual needs.", "Modern therapies customize treatments for patients.", "moslashtirmoq"),
                    ("immune", "/ɪˈmjuːn/", "adj.", "sifat (adjective)", "Resistant to a particular infection or toxin.", "Vaccines help people become immune to diseases.", "immunitetga ega, himoyalangan"),
                    ("diagnose", "/ˈdaɪəɡnəʊz/", "v.", "fe'l (verb)", "To identify the nature of an illness.", "The doctor was able to diagnose the condition early.", "tashxis qo'ymoq"),
                    ("symptom", "/ˈsɪmptəm/", "n.", "ot (noun)", "A physical or mental sign indicating a disease.", "Fever and cough are common symptoms of flu.", "alomat, simptom"),
                    ("remedy", "/ˈremədi/", "n.", "ot (noun)", "A medicine or treatment for disease.", "Honey and tea is a traditional remedy for colds.", "dori, davo"),
                    ("prescribe", "/prɪˈskraɪb/", "v.", "fe'l (verb)", "To recommend a medicine or treatment officially.", "The physician prescribed antibiotics for the infection.", "dori yozib bermoq"),
                    ("infection", "/ɪnˈfekʃn/", "n.", "ot (noun)", "The invasion of body tissues by microorganisms.", "Clean bandages help prevent bacterial infection.", "infeksiya, yuqum"),
                    ("vital", "/ˈvaɪtl/", "adj.", "sifat (adjective)", "Extremely important or necessary for life.", "Oxygen is vital for human survival.", "o'ta muhim, hayotiy"),
                    ("recovery", "/rɪˈkʌvəri/", "n.", "ot (noun)", "A return to a normal state of health.", "She made a speedy recovery following surgery.", "tuzalish, tiklanish"),
                    ("fatigue", "/fəˈtiːɡ/", "n.", "ot (noun)", "Extreme tiredness resulting from mental or physical effort.", "He suffered from mental fatigue after exams.", "charchoq, horg'inlik")
                ]
            }
        ]
    },
    {
        "id": 8,
        "title": "Reading for the Real World 2",
        "cefr_level": "B2",
        "description": "Akademik matnlar va biznes, jamiyat mavzulari (Jony Academy dasturi, B2)",
        "units": [
            {
                "unit_number": 11,
                "title": "Differing Conceptions of Time (Vaqt tushunchalari)",
                "story": "Different cultures across the globe view time through fundamentally distinct lenses. In monochronic societies, punctuality is paramount, and people adhere strictly to schedules. In polychronic cultures, interpersonal relationships and flexibility take priority over rigid schedules. As globalization increases cross-cultural interaction, understanding these conflicting cultural perspectives becomes essential for international diplomacy and commerce.",
                "words": [
                    ("monochronic", "/ˌmɒnəˈkrɒnɪk/", "adj.", "sifat (adjective)", "Viewing time as linear, compartmentalized, and strictly scheduled.", "Monochronic cultures place heavy emphasis on punctuality.", "bir vaqtda bir ish qilishga asoslangan"),
                    ("punctuality", "/ˌpʌŋktʃuˈæləti/", "n.", "ot (noun)", "The quality of being prompt and on time.", "Punctuality is highly valued in Swiss business meetings.", "aniqlik, vaqtida bo'lish"),
                    ("paramount", "/ˈpærəmaʊnt/", "adj.", "sifat (adjective)", "More important than anything else; supreme.", "Safety on the construction site is of paramount importance.", "eng oliy, eng muhim"),
                    ("adhere", "/ədˈhɪər/", "v.", "fe'l (verb)", "To stick to a belief, rule, or schedule.", "Drivers must strictly adhere to speed limits.", "amal qilmoq, rioya etmoq"),
                    ("polychronic", "/ˌpɒlɪˈkrɒnɪk/", "adj.", "sifat (adjective)", "Viewing time as fluid and handling multiple tasks simultaneously.", "Polychronic negotiators value relationship-building over deadlines.", "ko'p vazifali, moslashuvchan vaqt"),
                    ("interpersonal", "/ˌɪntəˈpɜːsənl/", "adj.", "sifat (adjective)", "Relating to relationships between people.", "Strong interpersonal skills are essential for leaders.", "shaxslararo"),
                    ("rigid", "/ˈrɪdʒɪd/", "adj.", "sifat (adjective)", "Unable to bend; inflexible and strict.", "The company had rigid policies regarding work hours.", "qattiq, egilmas, qat'iy"),
                    ("perspective", "/pəˈspektɪv/", "n.", "ot (noun)", "A particular attitude toward or way of viewing something.", "Traveling abroad gives people a broader perspective on life.", "nuqtai nazar, dunyoqarash"),
                    ("globalization", "/ˌɡləʊbəlaɪˈzeɪʃn/", "n.", "ot (noun)", "The process by which businesses or cultures operate globally.", "Globalization has interconnected world economies.", "globallashuv"),
                    ("conflicting", "/kənˈflɪktɪŋ/", "adj.", "sifat (adjective)", "Incompatible or at variance with each other.", "The witnesses gave conflicting accounts of the incident.", "ziddiyatli, qarama-qarshi"),
                    ("diplomacy", "/dɪˈpləʊməsi/", "n.", "ot (noun)", "The profession or skill of managing international relations.", "International disputes must be resolved through diplomacy.", "diplomatiya"),
                    ("commerce", "/ˈkɒmɜːs/", "n.", "ot (noun)", "The activity of buying and selling; trade.", "Maritime commerce has flourished across the oceans.", "savdo-sotiq, tijorat"),
                    ("temporal", "/ˈtempərəl/", "adj.", "sifat (adjective)", "Relating to worldly time rather than eternity.", "Philosophers analyzed the temporal nature of human existence.", "vaqtinchalik, vaqtga oid"),
                    ("socialize", "/ˈsəʊʃəlaɪz/", "v.", "fe'l (verb)", "To mix socially with others.", "Coworkers often socialize after finishing their shifts.", "muloqot qilmoq, oshino bo'lmoq"),
                    ("civilization", "/ˌsɪvəlaɪˈzeɪʃn/", "n.", "ot (noun)", "An advanced state of human social development.", "Ancient civilizations developed agriculture along rivers.", "sivilizatsiya, madaniyat")
                ]
            },
            {
                "unit_number": 12,
                "title": "Corporate Social Responsibility (Korporativ Ijtimoiy Mas'uliyat)",
                "story": "Traditionally, the top priorities of corporations have been shareholder value and profitability. They placed little value on their company's environmental and social impact. However, this is changing. Thanks in part to commentary by consumers and activists, corporations around the world now realize that they can no longer turn a blind eye to the impact that their activities have on the world and its people. Forward-thinking companies actively integrate sustainable practices and ethical standards into their core business strategies.",
                "words": [
                    ("corporation", "/ˌkɔːpəˈreɪʃn/", "n.", "ot (noun)", "A large company or group of companies authorized to act as a single entity.", "Multinational corporations employ thousands of workers worldwide.", "korporatsiya, yirik kompaniya"),
                    ("shareholder", "/ˈʃeəhəʊldər/", "n.", "ot (noun)", "An owner of shares in a company.", "Shareholders voted to approve the new annual budget.", "aksiyador"),
                    ("profitability", "/ˌprɒfɪtəˈbɪləti/", "n.", "ot (noun)", "The degree to which a business or activity yields financial gain.", "The firm focused on maximizing long-term profitability.", "foydalilik, rentabellik"),
                    ("environmental", "/ɪnˌvaɪrənˈmentl/", "adj.", "sifat (adjective)", "Relating to the natural world and the impact of human activity on its condition.", "Companies face strict environmental regulations regarding waste.", "atrof-muhitga oid, ekologik"),
                    ("commentary", "/ˈkɒməntri/", "n.", "ot (noun)", "An expression of opinions or offering of explanations about an event or situation.", "Public commentary influenced the corporation's decision.", "sharh, fikr-mulohaza"),
                    ("activist", "/ˈæktɪvɪst/", "n.", "ot (noun)", "A person who campaigns to bring about political or social change.", "Environmental activists protested against deforestation.", "faol, faoliyat olib boruvchi"),
                    ("sustainable", "/səˈsteɪnəbl/", "adj.", "sifat (adjective)", "Able to be maintained at a certain rate without depleting natural resources.", "Solar power is a sustainable energy alternative.", "barqaror, tabiatni asrovchi"),
                    ("ethical", "/ˈeθɪkl/", "adj.", "sifat (adjective)", "Relating to moral principles or the branch of knowledge dealing with these.", "Ethical leaders refuse to deceive their consumers.", "axloqiy, insof bilan qilingan"),
                    ("exploit", "/ɪkˈsplɔɪt/", "v.", "fe'l (verb)", "To benefit unfairly from the work of others or to make full use of a resource.", "Companies must never exploit vulnerable laborers.", "ekspluatatsiya qilmoq, nohaq foydalanmoq"),
                    ("transparency", "/trænsˈpærənsi/", "n.", "ot (noun)", "The condition of being clear, open, and easy to examine or verify.", "Financial transparency builds trust with investors.", "shaffoflik, ochiqlik"),
                    ("philanthropy", "/fɪˈlænθrəpi/", "n.", "ot (noun)", "The desire to promote the welfare of others, expressed especially by the generous donation of money.", "The billionaire devoted his wealth to medical philanthropy.", "saxovatpeshalik, xayriya"),
                    ("obligation", "/ˌɒblɪˈɡeɪʃn/", "n.", "ot (noun)", "An act or course of action to which a person is morally or legally bound.", "Employers have a legal obligation to provide safety gear.", "majburiyat, burch"),
                    ("violate", "/ˈvaɪəleɪt/", "v.", "fe'l (verb)", "To break or act against something, especially a law, agreement, or principle.", "Dumping chemicals into rivers violates environmental law.", "buzmoq, xilof ish tutmoq"),
                    ("reputation", "/ˌrepjuˈteɪʃn/", "n.", "ot (noun)", "The beliefs or opinions that are generally held about someone or something.", "The scandal severely damaged the brand's reputation.", "obro'-e'tibor, nom"),
                    ("accountability", "/əˌkaʊntəˈbɪləti/", "n.", "ot (noun)", "The fact or condition of being accountable; responsibility.", "Democratic governance requires public accountability.", "javobgarlik, hisobdorlik")
                ]
            }
        ]
    },
    {
        "id": 9,
        "title": "IELTS & Academic Core Vocabulary",
        "cefr_level": "C1",
        "description": "IELTS 7.5 - 9.0 imtihonlari va akademik insholar uchun maxsus so'zlar",
        "units": [
            {
                "unit_number": 1,
                "title": "Scientific & Academic Analysis (Ilmiy tahlil)",
                "story": "Empirical methodology forms the cornerstone of academic research. Scholars must formulate rigorous hypotheses, gather quantifiable data, and objectively assess statistical correlations. Subjective bias can undermine the credibility of research findings, making peer review an indispensable safeguard in scientific inquiry.",
                "words": [
                    ("empirical", "/ɪmˈpɪrɪkl/", "adj.", "sifat (adjective)", "Based on observation or experience rather than theory.", "Empirical evidence substantiated the scientist's claims.", "tajribaga asoslangan, empirik"),
                    ("cornerstone", "/ˈkɔːnəstəʊn/", "n.", "ot (noun)", "An important quality or feature on which a particular thing is based.", "Honesty is the cornerstone of any healthy relationship.", "tamal toshi, asosiy tayanch"),
                    ("rigorous", "/ˈrɪɡərəs/", "adj.", "sifat (adjective)", "Extremely thorough, exhaustive, or accurate.", "The drug underwent rigorous clinical testing before release.", "qattiq, sinchkov, qat'iy"),
                    ("hypothesis", "/haɪˈpɒθəsɪs/", "n.", "ot (noun)", "A proposed explanation made as a starting point for further investigation.", "Researchers tested their hypothesis using laboratory experiments.", "gipoteza, ilmiy taxmin"),
                    ("quantifiable", "/ˈkwɒntɪfaɪəbl/", "adj.", "sifat (adjective)", "Able to be expressed or measured as a quantity.", "The benefits of remote work are readily quantifiable.", "o'lchasa bo'ladigan, hisoblanadigan"),
                    ("correlation", "/ˌkɒrəˈleɪʃn/", "n.", "ot (noun)", "A mutual relationship or connection between two or more things.", "Studies reveal a strong correlation between exercise and longevity.", "o'zaro bog'liqlik, korrelyatsiya"),
                    ("bias", "/ˈbaɪəs/", "n.", "ot (noun)", "Prejudice in favor of or against one thing compared with another.", "Researchers worked diligently to eliminate experimental bias.", "tarafgashlik, noxolislik"),
                    ("undermine", "/ˌʌndəˈmaɪn/", "v.", "fe'l (verb)", "To lessen the effectiveness, power, or ability of.", "Unsubstantiated rumors undermined consumer confidence.", "putur yetkazmoq, zaiflashtirmoq"),
                    ("credibility", "/ˌkredəˈbɪləti/", "n.", "ot (noun)", "The quality of being trusted and believed in.", "The witness lost all credibility after contradicting herself.", "ishonchlilik, e'tibor"),
                    ("indispensable", "/ˌɪndɪˈspensəbl/", "adj.", "sifat (adjective)", "Absolutely necessary; essential.", "A computer is an indispensable tool in modern research.", "ajralmas, zaruriy"),
                    ("scrutinize", "/ˈskruːtɪnaɪz/", "v.", "fe'l (verb)", "To examine or inspect closely and thoroughly.", "Auditors arrived to scrutinize the firm's financial accounts.", "sinchiklab tekshirmoq"),
                    ("substantiate", "/səbˈstænʃieɪt/", "v.", "fe'l (verb)", "To provide evidence to support or prove the truth of.", "The claimant failed to substantiate his accusations.", "isbotlamoq, dalillar bilan tasdiqlamoq"),
                    ("ambiguous", "/æmˈbɪɡjuəs/", "adj.", "sifat (adjective)", "Open to more than one interpretation; having a double meaning.", "The contract language was overly ambiguous and caused confusion.", "noaniq, ikki ma'noli"),
                    ("paradigm", "/ˈpærədaɪm/", "n.", "ot (noun)", "A typical example or pattern of something; a model.", "Quantum physics created a profound paradigm shift in science.", "paradigma, namuna, andoza"),
                    ("plausible", "/ˈplɔːzəbl/", "adj.", "sifat (adjective)", "Seeming reasonable or probable.", "She offered a completely plausible excuse for being absent.", "ishonarli, haqiqatga yaqin")
                ]
            }
        ]
    }
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for book in NEW_BOOKS:
        b_id = book["id"]
        # Insert or update book
        cur.execute("""
            INSERT INTO books (id, title, cefr_level, description)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                cefr_level = excluded.cefr_level,
                description = excluded.description
        """, (b_id, book["title"], book["cefr_level"], book["description"]))
        print(f"[+] Book {b_id} qo'shildi/yangilandi: {book['title']}")

        for u in book["units"]:
            u_num = u["unit_number"]
            cur.execute("""
                INSERT INTO units (book_id, unit_number, title, story)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(book_id, unit_number) DO UPDATE SET
                    title = excluded.title,
                    story = excluded.story
            """, (b_id, u_num, u["title"], u["story"]))
            
            # Fetch unit_id
            cur.execute("SELECT id FROM units WHERE book_id = ? AND unit_number = ?", (b_id, u_num))
            unit_id = cur.fetchone()[0]

            for idx, word_tuple in enumerate(u["words"]):
                w_idx = idx + 1
                word, phonetic, pos, pos_uz, defn, ex, tr_uz = word_tuple
                audio_url = f"https://dict.youdao.com/dictvoice?audio={word}&type=2"
                
                cur.execute("""
                    INSERT INTO words (book_id, unit_id, unit_number, word_index, word, phonetic, part_of_speech, part_of_speech_uz, definition, example, translation_uz, audio_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(book_id, unit_number, word_index) DO UPDATE SET
                        word = excluded.word,
                        phonetic = excluded.phonetic,
                        part_of_speech = excluded.part_of_speech,
                        part_of_speech_uz = excluded.part_of_speech_uz,
                        definition = excluded.definition,
                        example = excluded.example,
                        translation_uz = excluded.translation_uz,
                        audio_url = excluded.audio_url
                """, (b_id, unit_id, u_num, w_idx, word, phonetic, pos, pos_uz, defn, ex, tr_uz, audio_url))

            print(f"  [+] Book {b_id} Unit {u_num}: {u['title']} ({len(u['words'])} ta so'z yuklandi)")

    conn.commit()
    conn.close()
    print("\n✅ Yangi kitoblar va so'zlar SQLite bazaga muvaffaqiyatli saqlandi!")

if __name__ == "__main__":
    main()
