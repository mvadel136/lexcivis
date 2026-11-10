const AR = {
  skip: "انتقل إلى المحتوى",
  tagline: "دليل الإجراءات الإدارية في موريتانيا",
  nav_ask: "اسأل", nav_inst: "للمؤسسات",
  hello: "عن أي إجراء إداري تريد أن تسأل؟",
  hello_sub: "اكتب سؤالك بالعربية أو الحسانية أو الفرنسية. الإجابة منقولة من البطاقة الرسمية للإجراء، ويمكنك فتح مصدرها بجانبها.",
  ask_label: "سؤالك", placeholder: "مثلاً: كم تكلفة جواز السفر؟", send: "أرسل",
  plain: "صياغة مبسطة إضافية", reset: "محادثة جديدة", empty_q: "اكتب سؤالاً قبل الإرسال.",
  answered: "من البطاقة الرسمية", held: "النسختان الرسميتان مختلفتان", refused: "لا توجد بطاقة مطابقة", clarify: "حدّد الإجراء",
  dialect: "حسانية",
  held_explain: "النسخة العربية والنسخة الفرنسية من البطاقة لا تعطيان القيمة نفسها. لا نختار بدلاً منك: تأكد من الإدارة المعنية.",
  src_chip: (lang) => `البطاقة الرسمية، النسخة ${lang === "ar" ? "العربية" : "الفرنسية"}`,
  version: { ar: "النسخة العربية", fr: "النسخة الفرنسية" },
  updated: (d) => `حُدّثت البطاقة في ${d}`,
  page_short: (p) => `ص ${p}`, page_of_doc: (p, n) => `ص ${p} من ${n}`,
  times: (n) => `منشور ${n} مرات`,
  docs_title: "نصوص مرفقة بهذا الإجراء", cited_doc: "مذكور في الأساس القانوني",
  see_also: "إجراءات قريبة",
  plain_label: "صياغة آلية غير رسمية. البطاقة أعلاه هي المرجع.", plain_rejected: "استُبعدت الصياغة المبسطة",
  searching: "جارٍ البحث في 836 بطاقة رسمية…",
  error: "تعذّر البحث.", error_hint: "تأكد من أن خادم LexCivis يعمل، ثم أعد المحاولة.", retry: "أعد المحاولة",
  how_title: "كيف تُبنى الإجابة",
  how: ["يجد الإجراء المناسب بين 836 بطاقة رسمية بالعربية والفرنسية.",
    "ينقل القيمة حرفياً من البطاقة، ولا يكتبها نموذج لغوي.",
    "يبيّن مصدرها: البطاقة نفسها، أو صفحة النص القانوني أو الاستمارة المرفقة."],
  how_note: "إذا اختلفت النسختان العربية والفرنسية، يقول ذلك ولا يختار إحداهما.",
  how_hint: "اضغط على «البطاقة الرسمية» أو على نص مرفق في أي إجابة ليظهر هنا.",
  close: "إغلاق", record_kind: "البطاقة الرسمية", doc_kind: { legal_text: "نص قانوني", form: "استمارة" },
  cited: "القيمة المقتبسة", full_record: "البطاقة كاملة", attachments: "المرفقات",
  tech: "تفاصيل تقنية", trace_title: "مسار الإجابة",
  facts: { file: "الملف", entry: "المُدخل", version: "النسخة", id: "رقم البطاقة", field: "الحقل", updated: "آخر تحديث",
    original: "الملف الأصلي", pages: "الصفحات", text: "النص", sha: "بصمة SHA-256", used_by: "البطاقات المرتبطة" },
  copies: (n) => `و${n} نسخة من الملف نفسه باسم آخر`,
  text_layer: "طبقة النص في ملف PDF", ocr_text: (n, p) => `${n} من ${p} صفحة مقروءة بالتعرف الضوئي`,
  tab_page: "الصفحة", tab_text: "النص", prev: "الصفحة السابقة", next: "الصفحة التالية",
  page_of: (p, n) => `${p} / ${n}`,
  ocr_warn: "نص مستخرج بالتعرف الضوئي وقد يحتوي أخطاء. صورة الصفحة هي المرجع.",
  download: "تنزيل الملف الأصلي", loading: "جارٍ التحميل…",
  inst_title: "ما تكشفه البيانات الرسمية، وكيف تتصرف المؤسسات",
  inst_lead: "هذا الجزء موجّه للإدارات وللمدققين: مشكلات حقيقية في البيانات المنشورة، وتمرين يواجه فيه خمس مؤسسات ستة أخطاء متتالية تحت قواعد مكتوبة.",
  findings_title: "ما وجدناه في البيانات",
  f_conflict: (q) => `إجراءً يعطي رسوماً أو آجالاً مختلفة بين نسخته العربية ونسخته الفرنسية، من أصل ${q.pairs}.`,
  f_basis: () => "إجراءً لا يذكر أي أساس قانوني في أي من اللغتين.",
  f_docs: (l) => `ملفاً مرفقاً لا تمثل إلا ${l.documents} وثيقة متميزة: ${l.duplicates} نسخة مكررة، و${l.broken.length} مرفقات ليست وثائق، و${l.ocr_pages} صفحة ممسوحة بلا نص قرأناها بالتعرف الضوئي.`,
  f_dups: () => "إجراءً منشوراً مرتين بالعنوان نفسه.",
  examples_label: "أمثلة",
  exercise_title: "تمرين الحوكمة",
  exercise_lead: "ستة أحداث مؤرخة تصل إلى خمس مؤسسات. كل مقترح يمر بحارس الصلاحيات وقواعد الترتيب القانوني، وكل إجراء له أثر عام ينتظر قراراً بشرياً. يُختم السجل في النهاية.",
  run_all: "شغّل المراحل الست", use_llm: "مقترحات يكتبها نموذج لغوي",
  running: (s) => `التمرين جارٍ منذ ${s} ثانية. يمر كل سؤال عبر محرك البحث الحقيقي.`,
  summary: (n, b, h) => `${n} مراحل، ${b} إجراءات ممنوعة، ${h} في انتظار قرار بشري.`,
  ledger: (r) => `السجل: ${r.records} قيداً، سلسلة SHA-256 ${r.chain_ok ? "سليمة" : "معطوبة"}، التوقيع ${r.sealed ? "صالح" : "غير موجود"}.`,
  stage_sum: (a, h, r, b, w) => [a && `${a} إجابة`, h && `${h} معلّقة`, r && `${r} رفض`, b && `${b} ممنوع`, w && `${w} ينتظر قراراً بشرياً`].filter(Boolean).join("، "),
  day: (d) => `اليوم ${d}`,
  inject_title: "أضف حدثاً من عندك", inject_label: "ما الذي يحدث", inject_q_label: "سؤال مواطن (اختياري)", run_inject: "شغّل مع هذا الحدث",
  gaps_title: "الثغرات", gaps_lead: "ثغرات في السياسات والمعايير والتنفيذ، لكل منها دليل ومقترح ومثال من دولة أخرى.",
  gap_type: { policy: "سياسات", standards: "معايير", implementation: "تنفيذ" },
  g: { evidence: "الدليل", proposal: "المقترح", example: "في دول أخرى", readiness: "الجاهزية 2.0" },
  pipeline_title: "المطابقة مع مسار ITU-T Y.3172",
  v: { ALLOWED: "مسموح", AWAITING_HUMAN: "ينتظر قراراً بشرياً", BLOCKED_MANDATE: "ممنوع: خارج الصلاحيات", BLOCKED_ORDER: "ممنوع: خطوة قانونية سابقة ناقصة" },
  agents: { OPERATOR: "مشغّل الخدمة", PROCEDURE_OWNER: "الوزارة المسؤولة", DATA_PROTECTION: "سلطة حماية البيانات",
    CYBER_RESPONSE: "الفريق الوطني للاستجابة للحوادث", CLOUD_HOST: "المستضيف في الإمارات" },
  acts: { add_language_gap: "يسجّل ثغرة لغوية", flag_record_for_review: "يطلب مراجعة البطاقة", request_confirmation: "يطلب تأكيداً",
    notify_authority: "يُبلغ سلطة حماية البيانات", show_warning_to_users: "يعرض تحذيراً للمواطنين", publish_notice_draft: "يُعدّ بلاغاً عاماً",
    pause_feature: "يوقف الخدمة مؤقتاً", open_incident: "يفتح حادثاً", transfer_logs_abroad: "ينقل السجلات إلى الخارج",
    confirm_authoritative_value: "يؤكد القيمة الرسمية", request_record_update: "يطلب تحديث البطاقة", require_notification: "يشترط إبلاغاً مسبقاً",
    set_transfer_conditions: "يحدد شروط النقل", request_information: "يطلب معلومات", issue_warning: "يوجّه إنذاراً",
    issue_formal_notice: "يوجّه إعذاراً", order_interruption_of_processing: "يأمر بوقف المعالجة", order_data_blocking: "يأمر بإغلاق البيانات",
    refuse_new_purpose: "يرفض غرضاً جديداً", request_takedown: "يطلب حجب المرسل", report_location_of_data: "يبيّن مكان البيانات",
    provide_logs_to_controller: "يسلّم السجلات للمسؤول", delete_on_controller_order: "يحذف بأمر المسؤول",
    use_logs_for_training: "يدرّب نموذجه على السجلات", correct_answer_template: "يصحح نموذج الإجابة" },
  stage_titles: { S1: "الإطلاق: الخدمة تجيب المواطنين", S2: "نسختان رسميتان مختلفتان",
    S3: "بطاقة قديمة: إعلان مدة جديدة", S4: "أسئلة بالحسانية بالحرف العربي واللاتيني",
    S5: "بيانات شخصية واستضافة في الخارج وطلب تدريب", S6: "رسالة رسمية مزيفة", S7: "حدث تضيفه أنت" },
  pipeline: [
    ["SRC", "836 إجراءً بالعربية والفرنسية، و98 نصاً قانونياً واستمارة مرفقة، وأسئلة المواطنين"],
    ["C", "تحميل البطاقات، مطابقة الحقول، الربط بين النسختين، حذف المرفقات المكررة ببصمة SHA-256"],
    ["PP", "التوحيد، الحسانية ومفردات المواطنين، إخفاء البيانات الشخصية، التعرف الضوئي على النصوص الممسوحة، مقارنة النسختين"],
    ["M", "بحث هجين (BM25 وBGE-M3 ودمج RRF ومعيد ترتيب BGE)، مصنّف حقول مدرّب على البطاقات، الصفحة الأنسب من كل نص"],
    ["P", "الاستشهاد أو الرفض، التحقق من الحقل، تعليق الإجابة عند الاختلاف، حارس الصلاحيات، قواعد الترتيب القانوني، القرار البشري"],
    ["D", "واجهة برمجية وسطر أوامر"],
    ["SINK", "هذه الصفحة مع مصدر كل قيمة، وملف الحالة المقدم للمؤسسات"],
    ["MLFO", "منسق يوجهه هدف التعلم الآلي (ml_intent.yaml)، مع المصدر وسجل SHA-256 موقّع"],
    ["Sandbox", "ستة أحداث مؤرخة وحدث يضيفه المستخدم مباشرة"]],
  foot: "نموذج أولي مستقل مبني على البيانات العامة للإجراءات الإدارية الموريتانية والقانون 2017-020. الأحداث الموسومة «محاكاة» خيالية.",
  health: (h) => `الإصدار ${h.version}، ${h.procedures} إجراء`,
  examples: ["كم تكلفة جواز السفر العادي؟", "ما هي مدة معالجة طلب رخصة نقل المحروقات؟", "كم يكلف الطابع للحصول على معلومات حول رسم عقاري؟", "شنهِ لوراق الِّ لازمين باش نخرج بطاگة التعريف؟"],
};

const FR = {
  skip: "Aller au contenu",
  tagline: "Guide des démarches administratives en Mauritanie",
  nav_ask: "Demander", nav_inst: "Pour les institutions",
  hello: "Sur quelle démarche voulez-vous une réponse ?",
  hello_sub: "Écrivez en français, en arabe ou en hassaniya. La réponse reprend la fiche officielle de la procédure, et sa source s'ouvre à côté.",
  ask_label: "Votre question", placeholder: "Par exemple : combien coûte le passeport ?", send: "Envoyer",
  plain: "Reformulation simple en plus", reset: "Nouvelle conversation", empty_q: "Écrivez une question avant d'envoyer.",
  answered: "D'après la fiche officielle", held: "Les deux versions officielles diffèrent", refused: "Aucune fiche ne correspond", clarify: "Précisez la démarche",
  dialect: "hassaniya",
  held_explain: "La version arabe et la version française de la fiche ne donnent pas la même valeur. Nous ne choisissons pas à votre place : vérifiez auprès de l'administration.",
  src_chip: (lang) => `Fiche officielle, version ${lang === "ar" ? "arabe" : "française"}`,
  version: { ar: "version arabe", fr: "version française" },
  updated: (d) => `Fiche mise à jour le ${d}`,
  page_short: (p) => `p. ${p}`, page_of_doc: (p, n) => `p. ${p} sur ${n}`,
  times: (n) => `publié ${n} fois`,
  docs_title: "Textes joints à cette démarche", cited_doc: "cité comme base juridique",
  see_also: "Démarches proches",
  plain_label: "Reformulation automatique, non officielle. La fiche ci-dessus fait foi.", plain_rejected: "Reformulation écartée",
  searching: "Recherche dans les 836 fiches officielles…",
  error: "La recherche n'a pas abouti.", error_hint: "Vérifiez que le serveur LexCivis tourne, puis réessayez.", retry: "Réessayer",
  how_title: "Comment la réponse est construite",
  how: ["Trouver la bonne démarche parmi 836 fiches officielles, en arabe et en français.",
    "Recopier la valeur mot pour mot depuis la fiche : aucun modèle de langue ne l'écrit.",
    "Montrer d'où elle vient : la fiche elle-même, ou la page du texte juridique ou du formulaire joint."],
  how_note: "Si les versions arabe et française ne disent pas la même chose, il le signale au lieu de choisir.",
  how_hint: "Cliquez sur « Fiche officielle » ou sur un texte joint dans une réponse pour l'afficher ici.",
  close: "Fermer", record_kind: "Fiche officielle", doc_kind: { legal_text: "Texte juridique", form: "Formulaire" },
  cited: "Valeur citée", full_record: "Fiche complète", attachments: "Pièces jointes",
  tech: "Détails techniques", trace_title: "Parcours de la réponse",
  facts: { file: "Fichier", entry: "Entrée", version: "Version", id: "Numéro de fiche", field: "Champ", updated: "Mise à jour",
    original: "Fichier d'origine", pages: "Pages", text: "Texte", sha: "Empreinte SHA-256", used_by: "Fiches liées" },
  copies: (n) => `et ${n} copie(s) du même fichier sous un autre nom`,
  text_layer: "couche texte du PDF", ocr_text: (n, p) => `${n} page(s) sur ${p} lues par OCR`,
  tab_page: "Page", tab_text: "Texte", prev: "Page précédente", next: "Page suivante",
  page_of: (p, n) => `${p} / ${n}`,
  ocr_warn: "Texte obtenu par reconnaissance optique : il peut contenir des erreurs. L'image de la page fait foi.",
  download: "Télécharger le fichier d'origine", loading: "Chargement…",
  inst_title: "Ce que révèlent les données officielles, et comment réagissent les institutions",
  inst_lead: "Cette partie s'adresse aux administrations et aux auditeurs : de vrais problèmes dans les données publiées, et un exercice où cinq institutions font face à six incidents successifs, sous des règles écrites.",
  findings_title: "Ce que nous avons trouvé",
  f_conflict: (q) => `procédures donnent un frais ou un délai différent entre la version arabe et la version française, sur ${q.pairs}.`,
  f_basis: () => "procédures ne citent aucune base juridique, dans aucune des deux langues.",
  f_docs: (l) => `fichiers joints ne correspondent qu'à ${l.documents} documents distincts : ${l.duplicates} copies, ${l.broken.length} pièces qui ne sont pas des documents, et ${l.ocr_pages} pages scannées sans texte, lues ici par OCR.`,
  f_dups: () => "procédures sont publiées deux fois sous le même titre.",
  examples_label: "Exemples",
  exercise_title: "Exercice de gouvernance",
  exercise_lead: "Six événements datés arrivent à cinq institutions. Chaque proposition passe par le contrôle des mandats et de l'ordre légal ; tout acte ayant un effet public attend une décision humaine. Le registre est scellé à la fin.",
  run_all: "Lancer les six étapes", use_llm: "Propositions rédigées par un modèle de langue",
  running: (s) => `Exercice en cours depuis ${s} s. Chaque question passe par le vrai moteur de recherche.`,
  summary: (n, b, h) => `${n} étapes, ${b} actions bloquées, ${h} en attente d'une décision humaine.`,
  ledger: (r) => `Registre : ${r.records} enregistrements, chaîne SHA-256 ${r.chain_ok ? "vérifiée" : "CASSÉE"}, signature ${r.sealed ? "valide" : "absente"}.`,
  stage_sum: (a, h, r, b, w) => [a && `${a} réponse(s)`, h && `${h} suspendue(s)`, r && `${r} refus`, b && `${b} bloquée(s)`, w && `${w} en attente d'un humain`].filter(Boolean).join(", "),
  day: (d) => `Jour ${d}`,
  inject_title: "Ajouter votre propre événement", inject_label: "Ce qui se passe", inject_q_label: "Question d'un citoyen (facultatif)", run_inject: "Lancer avec cet événement",
  gaps_title: "Lacunes", gaps_lead: "Lacunes de politique, de normes et de mise en œuvre, chacune avec une preuve, une proposition et un exemple étranger.",
  gap_type: { policy: "politique", standards: "normes", implementation: "mise en œuvre" },
  g: { evidence: "Preuve", proposal: "Proposition", example: "Ailleurs", readiness: "Readiness 2.0" },
  pipeline_title: "Correspondance avec le pipeline ITU-T Y.3172",
  v: { ALLOWED: "Autorisé", AWAITING_HUMAN: "Attend une décision humaine", BLOCKED_MANDATE: "Bloqué : hors mandat", BLOCKED_ORDER: "Bloqué : étape légale préalable manquante" },
  agents: { OPERATOR: "Opérateur du service", PROCEDURE_OWNER: "Ministère responsable", DATA_PROTECTION: "Autorité de protection des données",
    CYBER_RESPONSE: "Équipe nationale de réponse aux incidents", CLOUD_HOST: "Hébergeur aux Émirats" },
  acts: { add_language_gap: "note une lacune de langue", flag_record_for_review: "signale la fiche pour révision", request_confirmation: "demande une confirmation",
    notify_authority: "informe l'autorité de protection des données", show_warning_to_users: "affiche un avertissement aux citoyens",
    publish_notice_draft: "prépare un communiqué public", pause_feature: "suspend le service", open_incident: "ouvre un incident",
    transfer_logs_abroad: "transfère les journaux à l'étranger", confirm_authoritative_value: "confirme la valeur officielle",
    request_record_update: "demande la mise à jour de la fiche", require_notification: "exige une notification préalable",
    set_transfer_conditions: "fixe les conditions du transfert", request_information: "demande des informations",
    issue_warning: "adresse un avertissement", issue_formal_notice: "adresse une mise en demeure",
    order_interruption_of_processing: "ordonne l'interruption du traitement", order_data_blocking: "ordonne le verrouillage des données",
    refuse_new_purpose: "refuse une nouvelle finalité", request_takedown: "demande le blocage de l'expéditeur",
    report_location_of_data: "indique où sont les données", provide_logs_to_controller: "remet les journaux au responsable",
    delete_on_controller_order: "supprime sur ordre du responsable", use_logs_for_training: "entraîne son propre modèle sur les journaux",
    correct_answer_template: "corrige le modèle de réponse" },
  stage_titles: { S1: "Lancement : le service répond aux citoyens", S2: "Deux versions officielles qui diffèrent",
    S3: "Fiche périmée : un nouveau délai est annoncé", S4: "Questions en hassaniya, en écriture arabe et latine",
    S5: "Données personnelles, hébergement à l'étranger et demande d'entraînement", S6: "Un faux message officiel", S7: "Votre propre événement" },
  pipeline: [
    ["SRC", "836 procédures en arabe et en français, 98 textes juridiques et formulaires joints, questions des citoyens"],
    ["C", "Chargement des fiches, correspondance des champs, appariement des deux versions, dédoublonnage des pièces jointes par SHA-256"],
    ["PP", "Normalisation, hassaniya et vocabulaire citoyen, masquage des données personnelles, OCR des textes scannés, contrôle arabe/français"],
    ["M", "Recherche hybride (BM25, BGE-M3, fusion RRF, reranker BGE), classifieur de champ entraîné sur les fiches, page la plus pertinente de chaque texte"],
    ["P", "Citer ou refuser, vérification du champ, réponse suspendue en cas d'écart, garde-fou des mandats, règles d'ordre légal, décision humaine"],
    ["D", "API et ligne de commande"],
    ["SINK", "Cette page, avec la source de chaque valeur, et le dossier de cas remis aux institutions"],
    ["MLFO", "Orchestrateur guidé par l'intention ML (ml_intent.yaml), provenance, registre SHA-256 signé"],
    ["Sandbox", "Six événements datés et un événement ajouté en direct"]],
  foot: "Prototype indépendant, construit sur les données publiques des démarches administratives de Mauritanie et la loi 2017-020. Les événements marqués « simulé » sont fictifs.",
  health: (h) => `Version ${h.version}, ${h.procedures} procédures`,
  examples: ["Combien coûte le passeport ?", "Combien coûte le timbre pour des renseignements sur un titre foncier ?", "Quelle est la base juridique pour l'agrément d'une agence de voyages ?", "gaddach casier judiciaire bulletin 3 ?"],
};

const EN = {
  skip: "Skip to content",
  tagline: "Mauritania's administrative procedures, answered from the official records",
  nav_ask: "Ask", nav_inst: "For institutions",
  hello: "Which administrative procedure do you need?",
  hello_sub: "Questions are asked in Arabic, Hassaniya or French, as citizens do. The answer is copied from the procedure's official record, and its source opens beside it.",
  ask_label: "Your question", placeholder: "Ask in Arabic, French or Hassaniya", send: "Send",
  plain: "Add a plain-language version", reset: "New conversation", empty_q: "Type a question first.",
  answered: "From the official record", held: "The two official versions disagree", refused: "No matching record", clarify: "Which procedure?",
  dialect: "Hassaniya",
  held_explain: "The Arabic and French versions of the record give different values. LexCivis does not choose for the citizen: the administration has to confirm.",
  src_chip: (lang) => `Official record, ${lang === "ar" ? "Arabic" : "French"} version`,
  version: { ar: "Arabic version", fr: "French version" },
  updated: (d) => `Record last updated ${d}`,
  page_short: (p) => `p. ${p}`, page_of_doc: (p, n) => `p. ${p} of ${n}`,
  times: (n) => `published ${n} times`,
  docs_title: "Texts attached to this procedure", cited_doc: "cited as legal basis",
  see_also: "Related procedures",
  plain_label: "Automatic plain-language version, not official. The record above is authoritative.", plain_rejected: "Plain-language version rejected",
  searching: "Searching 836 official records…",
  error: "The search failed.", error_hint: "Check that the LexCivis server is running, then try again.", retry: "Try again",
  how_title: "How an answer is built",
  how: ["Find the right procedure among 836 official records, in Arabic and French.",
    "Copy the value word for word from the record. No language model writes it.",
    "Show where it comes from: the record itself, or the page of the attached legal text or form."],
  how_note: "When the Arabic and French versions disagree, it says so instead of picking one.",
  how_hint: "Click “Official record” or an attached text in any answer to open it here.",
  close: "Close", record_kind: "Official record", doc_kind: { legal_text: "Legal text", form: "Form" },
  cited: "Cited value", full_record: "Full record", attachments: "Attachments",
  tech: "Technical details", trace_title: "How the answer was found",
  facts: { file: "File", entry: "Entry", version: "Version", id: "Record id", field: "Field", updated: "Last update",
    original: "Original file", pages: "Pages", text: "Text", sha: "SHA-256", used_by: "Linked records" },
  copies: (n) => `and ${n} copies of the same file under other names`,
  text_layer: "PDF text layer", ocr_text: (n, p) => `${n} of ${p} pages read by OCR`,
  tab_page: "Page", tab_text: "Text", prev: "Previous page", next: "Next page",
  page_of: (p, n) => `${p} / ${n}`,
  ocr_warn: "Text read by optical character recognition and may contain errors. The page image is authoritative.",
  download: "Download the original file", loading: "Loading…",
  inst_title: "What the official data shows, and how institutions respond",
  inst_lead: "For administrations and auditors: real problems found in the published data, and an exercise in which five institutions face six staged incidents under written rules.",
  findings_title: "What we found in the data",
  f_conflict: (q) => `procedures give a different fee or delay in their Arabic and French versions, out of ${q.pairs}.`,
  f_basis: () => "procedures cite no legal basis in either language.",
  f_docs: (l) => `attached files are only ${l.documents} distinct documents: ${l.duplicates} copies, ${l.broken.length} attachments that are not documents, and ${l.ocr_pages} scanned pages without text, read here by OCR.`,
  f_dups: () => "procedures are published twice under the same title.",
  examples_label: "Examples",
  exercise_title: "Governance exercise",
  exercise_lead: "Six dated events reach five institutions. Every proposal goes through a mandate guard and legal-order rules, and every act with public effect waits for a human decision. The ledger is sealed at the end.",
  run_all: "Run the six stages", use_llm: "Proposals drafted by a language model",
  running: (s) => `Exercise running for ${s} s. Every question goes through the real search engine.`,
  summary: (n, b, h) => `${n} stages, ${b} actions blocked, ${h} waiting for a human decision.`,
  ledger: (r) => `Ledger: ${r.records} records, SHA-256 chain ${r.chain_ok ? "verified" : "BROKEN"}, signature ${r.sealed ? "valid" : "missing"}.`,
  stage_sum: (a, h, r, b, w) => [a && `${a} answered`, h && `${h} held`, r && `${r} refused`, b && `${b} blocked`, w && `${w} waiting for a human`].filter(Boolean).join(", "),
  day: (d) => `Day ${d}`,
  inject_title: "Add your own event", inject_label: "What happens", inject_q_label: "A citizen's question (optional)", run_inject: "Run with this event",
  gaps_title: "Gaps", gaps_lead: "Policy, standards and implementation gaps, each with evidence, a proposal and an example from another country.",
  gap_type: { policy: "policy", standards: "standards", implementation: "implementation" },
  g: { evidence: "Evidence", proposal: "Proposal", example: "Elsewhere", readiness: "Readiness 2.0" },
  pipeline_title: "Mapping to the ITU-T Y.3172 pipeline",
  v: { ALLOWED: "Allowed", AWAITING_HUMAN: "Waiting for a human", BLOCKED_MANDATE: "Blocked: outside mandate", BLOCKED_ORDER: "Blocked: a prior legal step is missing" },
  agents: { OPERATOR: "Service operator", PROCEDURE_OWNER: "Responsible ministry", DATA_PROTECTION: "Data-protection authority",
    CYBER_RESPONSE: "National incident response team", CLOUD_HOST: "Hosting provider in the UAE" },
  acts: { add_language_gap: "records a language gap", flag_record_for_review: "flags the record for review", request_confirmation: "asks for confirmation",
    notify_authority: "informs the data-protection authority", show_warning_to_users: "shows a warning to citizens",
    publish_notice_draft: "drafts a public notice", pause_feature: "pauses the service", open_incident: "opens an incident",
    transfer_logs_abroad: "transfers the logs abroad", confirm_authoritative_value: "confirms the official value",
    request_record_update: "asks for the record to be updated", require_notification: "requires prior notification",
    set_transfer_conditions: "sets the transfer conditions", request_information: "requests information",
    issue_warning: "issues a warning", issue_formal_notice: "issues a formal notice",
    order_interruption_of_processing: "orders processing to stop", order_data_blocking: "orders the data to be blocked",
    refuse_new_purpose: "refuses a new purpose", request_takedown: "asks to block the sender",
    report_location_of_data: "reports where the data is", provide_logs_to_controller: "hands the logs to the controller",
    delete_on_controller_order: "deletes on the controller's order", use_logs_for_training: "trains its own model on the logs",
    correct_answer_template: "corrects the answer template" },
  stage_titles: { S1: "Launch: the service answers citizens", S2: "Two official versions that disagree",
    S3: "Outdated record: a new delay is announced", S4: "Questions in Hassaniya, in Arabic and Latin script",
    S5: "Personal data, hosting abroad and a training request", S6: "A fake official message", S7: "Your own event" },
  pipeline: [
    ["SRC", "836 procedures in Arabic and French, 98 attached legal texts and forms, citizens' questions"],
    ["C", "Loading the records, field mapping, pairing the two versions, SHA-256 deduplication of attachments"],
    ["PP", "Normalisation, Hassaniya and citizen wording, personal-data masking, OCR of scanned texts, Arabic/French check"],
    ["M", "Hybrid search (BM25, BGE-M3, RRF fusion, BGE reranker), a field classifier trained on the records, best page of each text"],
    ["P", "Cite or refuse, field verification, hold on disagreement, mandate guard, legal-order rules, human decision"],
    ["D", "API and command line"],
    ["SINK", "This page, with the source of every value, and the case brief for institutions"],
    ["MLFO", "Orchestrator driven by the ML intent (ml_intent.yaml), provenance, signed SHA-256 ledger"],
    ["Sandbox", "Six dated events and an event added live"]],
  foot: "Independent prototype built on Mauritania's public administrative-procedure data and Law 2017-020. Events marked SIMULATED are fictional.",
  health: (h) => `Version ${h.version}, ${h.procedures} procedures`,
  examples: ["كم تكلفة جواز السفر العادي؟", "Combien coûte le timbre pour des renseignements sur un titre foncier ?", "ما هي مدة معالجة طلب رخصة نقل المحروقات؟", "gaddach casier judiciaire bulletin 3 ?"],
};

const I18N = { ar: AR, fr: FR, en: EN };
const LOOSE = { a: "[aàâä]", e: "[eéèêë]", i: "[iîï]", o: "[oôö]", u: "[uùûü]", c: "[cç]", "ا": "[اأإآ]", "ه": "[هة]", "ي": "[يى]" };
const DOC_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/></svg>';

let lang = "ar";
let health = null;
let lastRun = null;
let evidenceState = null;
const exchanges = [];
const cache = {};
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const t = (k, ...args) => {
  const v = I18N[lang][k] ?? EN[k] ?? k;
  return typeof v === "function" ? v(...args) : v;
};

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function dirOf(text) {
  return /[؀-ۿ]/.test(text || "") ? "rtl" : "ltr";
}

function langAttrs(text) {
  const d = dirOf(text);
  return `lang="${d === "rtl" ? "ar" : "fr"}" dir="${d}"`;
}

function remember(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    localStorage.setItem(key, value);
  } catch {
    return null;
  }
  return value;
}

async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!r.ok) {
    const detail = await r.json().then((j) => j.detail).catch(() => "");
    throw new Error(typeof detail === "string" && detail ? detail : `HTTP ${r.status}`);
  }
  return r.json();
}

function cached(path) {
  cache[path] = cache[path] || api(path).catch((e) => { delete cache[path]; throw e; });
  return cache[path];
}

function pickLanguage() {
  const asked = new URLSearchParams(location.search).get("lang");
  if (I18N[asked]) return asked;
  const saved = remember("lexcivis-lang");
  if (I18N[saved]) return saved;
  for (const l of navigator.languages || [navigator.language || ""]) {
    const code = l.slice(0, 2).toLowerCase();
    if (I18N[code]) return code;
  }
  return "en";
}

function wide() {
  return matchMedia("(min-width: 1080px)").matches;
}

function docked() {
  return wide() && document.body.dataset.view === "ask";
}

function setLang(next) {
  lang = next;
  remember("lexcivis-lang", next);
  document.documentElement.lang = next;
  document.documentElement.dir = next === "ar" ? "rtl" : "ltr";
  $$("[data-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === next)));
  $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  $$("[data-i18n-label]").forEach((el) => el.setAttribute("aria-label", t(el.dataset.i18nLabel)));
  if (health) $("#health").textContent = t("health", health);
  $("#examples").innerHTML = t("examples").map((q) => `<li><button type="button" class="chip example" ${langAttrs(q)}>${esc(q)}</button></li>`).join("");
  renderThread();
  renderEvidence();
  loadInstitutions().catch(() => {});
  if (lastRun) $("#run-output").innerHTML = renderRun(lastRun);
}

function setView(view) {
  document.body.dataset.view = view;
  $$(".views [data-view]").forEach((b) => (b.dataset.view === view ? b.setAttribute("aria-current", "page") : b.removeAttribute("aria-current")));
  $("#view-ask").hidden = view !== "ask";
  $("#view-inst").hidden = view !== "inst";
  closeEvidence();
}

function splitList(value) {
  const parts = value.split(/\s*(?:•|[;؛]\s*-|^\s*-|\n-)\s*/).map((p) => p.trim()).filter((p) => p.length > 1);
  return parts.length > 1 ? `<ul class="checklist" ${langAttrs(value)}>${parts.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>` : `<p class="value-text" ${langAttrs(value)}>${esc(value)}</p>`;
}

function sourceChip(ref) {
  return `<button type="button" class="source" data-open="record" data-entry="${ref.entry}" data-lang="${esc(ref.lang)}" data-field="${esc(ref.field || "")}">${DOC_ICON.replace("M14 3v4h4", "M9 12h6M9 16h6")}${esc(t("src_chip", ref.lang))}</button>`;
}

function valueBlock(i) {
  if (i.field === "documents") return splitList(i.value);
  return `<p class="${i.value.length <= 70 ? "value-big" : "value-text"}" ${langAttrs(i.value)}>${esc(i.value)}</p>`;
}

function itemBlock(i) {
  if (i.held) {
    return `<div class="item"><p class="item-label">${esc(i.label)}</p>
      <div class="twins">
        <div class="twin" lang="ar" dir="rtl"><p class="twin-lang">العربية</p><p class="value-big">${esc(i.ar_value)}</p>${sourceChip(i.ar_source)}</div>
        <div class="twin" lang="fr" dir="ltr"><p class="twin-lang">Français</p><p class="value-big">${esc(i.fr_value)}</p>${sourceChip(i.source)}</div>
      </div></div>`;
  }
  return `<div class="item"><p class="item-label">${esc(i.label)}</p>${valueBlock(i)}${sourceChip(i.source)}</div>`;
}

function docChip(d) {
  return `<li><button type="button" class="doc" data-open="doc" data-id="${esc(d.id)}" data-page="${d.best.page}" data-terms="${esc((d.best.matched || []).join(" "))}">${DOC_ICON}
    <span class="doc-name" ${langAttrs(d.label)}>${esc(d.label)}</span>
    <span class="doc-meta">${esc(t("doc_kind")[d.kind] || "")}${d.relation === "cited" ? `, ${esc(t("cited_doc"))}` : ""}, ${esc(t("page_of_doc", d.best.page, d.pages))}</span></button></li>`;
}

function pickChips(a, i) {
  return a.alternatives.map((x) => `<li><button type="button" class="chip pick" data-index="${i}" data-title="${esc(x.title)}" ${langAttrs(x.title)}>${esc(x.title)}</button></li>`).join("");
}

function renderAnswer(a, i) {
  const badge = `<p class="badge ${a.status}">${esc(t(a.status))}${a.hassaniya ? `<span class="dialect">${esc(t("dialect"))}</span>` : ""}</p>`;
  if (a.status === "refused") {
    const lines = a.text.split("\n").filter(Boolean).map((l) => `<p ${langAttrs(l)}>${esc(l)}</p>`).join("");
    return `<article class="answer refused">${badge}${lines}</article>`;
  }
  if (a.status === "clarify") {
    return `<article class="answer clarify">${badge}<p ${langAttrs(a.text)}>${esc(a.text.split("\n")[0])}</p><ul class="chips">${pickChips(a, i)}</ul></article>`;
  }
  const p = a.plain || {};
  const notes = [
    ...(a.status === "held" ? [`<p class="note hold">${esc(t("held_explain"))}</p>`] : []),
    ...a.notes.filter((n) => !n.startsWith("Les versions officielles") && !n.startsWith("النسختان") && !/mise à jour le|تحديث|حدثت/.test(n))
      .map((n) => `<p class="note ${/ne figure pas|غير موجود/.test(n) ? "warn" : ""}" ${langAttrs(n)}>${esc(n)}</p>`),
    ...(p.reason && !p.accepted ? [`<p class="note">${esc(t("plain_rejected"))}: <span lang="en" dir="ltr">${esc(p.reason)}</span></p>`] : []),
  ].join("");
  const plain = p.accepted ? `<div class="plain" ${langAttrs(p.text)}><p class="plain-label">${esc(t("plain_label"))}</p><p>${esc(p.text)}</p></div>` : "";
  const docs = (a.documents || []).length ? `<div class="docs"><p class="docs-title">${esc(t("docs_title"))}</p><ul class="docs-list">${a.documents.map(docChip).join("")}</ul></div>` : "";
  const also = a.alternatives.length ? `<div class="also"><p>${esc(t("see_also"))}</p><ul class="chips small">${pickChips(a, i)}</ul></div>` : "";
  return `<article class="answer ${a.status}">${badge}
    <h3 tabindex="-1" ${langAttrs(a.title)}>${esc(a.title)}</h3>
    <p class="ministry" ${langAttrs(a.ministry)}>${esc(a.ministry)}</p>
    ${a.items.map(itemBlock).join("")}
    ${notes}${plain}${docs}
    ${a.last_update ? `<p class="updated">${esc(t("updated", a.last_update))}</p>` : ""}
    ${also}</article>`;
}

function renderExchange(x, i) {
  let body = `<p class="waiting" role="status"><span class="dots" aria-hidden="true"><span></span><span></span><span></span></span>${esc(t("searching"))}</p>`;
  if (x.answer) body = renderAnswer(x.answer, i);
  if (x.error) body = `<div class="answer failed" role="alert"><p><b>${esc(t("error"))}</b> ${esc(t("error_hint"))}</p><p class="small" dir="ltr" lang="en">${esc(x.error)}</p><button type="button" class="secondary retry" data-index="${i}">${esc(t("retry"))}</button></div>`;
  return `<section class="exchange" data-index="${i}"><p class="question" ${langAttrs(x.question)}>${esc(x.question)}</p>${body}</section>`;
}

function renderThread() {
  const thread = $("#thread");
  $$(".exchange", thread).forEach((el) => el.remove());
  thread.insertAdjacentHTML("beforeend", exchanges.map(renderExchange).join(""));
  $("#hello").hidden = exchanges.length > 0;
  $("#reset").hidden = exchanges.length === 0;
}

function setBusy(busy) {
  $$("#ask-form button, .example, .pick").forEach((b) => { b.disabled = busy; });
}

async function ask(question, index = null) {
  const i = index ?? exchanges.push({ question }) - 1;
  const x = exchanges[i];
  x.answer = null;
  x.error = null;
  const draw = () => {
    const old = $(`.exchange[data-index="${i}"]`);
    const html = renderExchange(x, i);
    if (old) old.outerHTML = html; else $("#thread").insertAdjacentHTML("beforeend", html);
    $("#hello").hidden = true;
    $("#reset").hidden = false;
    return $(`.exchange[data-index="${i}"]`);
  };
  setBusy(true);
  draw().scrollIntoView({ block: "end" });
  try {
    x.answer = await api("/api/ask", { question, plain: $("#plain").checked });
  } catch (e) {
    x.error = e.message;
  } finally {
    setBusy(false);
  }
  const el = draw();
  el.scrollIntoView({ block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  const heading = $("h3", el);
  if (heading) heading.focus({ preventScroll: true });
}

function highlight(text, terms) {
  const html = esc(text);
  const words = [...new Set(terms)].filter((w) => w.length > 2).sort((a, b) => b.length - a.length);
  if (!words.length) return html;
  const loose = (w) => [...w].map((c) => LOOSE[c] || c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("");
  return html.replace(new RegExp(`(${words.map(loose).join("|")})`, "giu"), "<mark>$1</mark>");
}

function openEvidence(state) {
  evidenceState = state;
  const ev = $("#evidence");
  ev.classList.add("open");
  ev.classList.toggle("sheet", !docked());
  $("#scrim").hidden = docked();
  $("#ev-close").hidden = false;
  renderEvidence();
  ev.focus({ preventScroll: true });
}

function closeEvidence() {
  const ev = $("#evidence");
  ev.classList.remove("sheet", "open");
  $("#scrim").hidden = true;
  $("#ev-close").hidden = true;
  $$(".source.active, .doc.active").forEach((x) => x.classList.remove("active"));
  evidenceState = null;
  renderEvidence();
}

function renderEvidence() {
  if (!evidenceState) {
    $("#ev-kind").textContent = "";
    $("#ev-title").textContent = t("how_title");
    $("#ev-title").removeAttribute("dir");
    $("#ev-body").innerHTML = `<ol class="how">${t("how").map((s) => `<li>${esc(s)}</li>`).join("")}</ol><p class="how-note">${esc(t("how_note"))}</p><p class="hint">${esc(t("how_hint"))}</p>`;
    return;
  }
  if (evidenceState.kind === "record") showRecord(evidenceState);
  if (evidenceState.kind === "doc") showDocument(evidenceState);
}

function factsList(rows) {
  return `<dl class="facts">${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join("")}</dl>`;
}

async function showRecord(state) {
  $("#ev-kind").textContent = t("record_kind");
  $("#ev-title").textContent = t("loading");
  $("#ev-body").innerHTML = "";
  try {
    const s = await cached(`/api/sources/${state.entry}/${state.lang}`);
    if (evidenceState !== state) return;
    const r = s.record;
    const f = t("facts");
    const fields = Object.entries(r.fields || {});
    const cited = fields.find(([label]) => label === state.field);
    const rest = fields.filter(([label]) => label !== state.field);
    const dir = state.lang === "ar" ? "rtl" : "ltr";
    const att = (r.attachments || []).filter((x) => x.document).map((x) => `<li><button type="button" class="doc" data-open="doc" data-id="${esc(x.document)}" data-page="1">${DOC_ICON}<span class="doc-name" ${langAttrs(x.label)}>${esc(x.label || x.file)}</span></button></li>`).join("");
    $("#ev-title").textContent = r.title;
    $("#ev-title").setAttribute("dir", dirOf(r.title));
    $("#ev-body").innerHTML = `
      <p class="ev-sub">${esc(t("version")[s.lang])}${r.ministry ? `, <span ${langAttrs(r.ministry)}>${esc(r.ministry)}</span>` : ""}</p>
      ${cited ? `<div class="cited" dir="${dir}" lang="${state.lang}"><p class="cited-tag">${esc(t("cited"))}</p><p class="cited-label">${esc(cited[0])}</p><p class="cited-value">${esc(cited[1])}</p></div>` : ""}
      <h3>${esc(t("full_record"))}</h3>
      <dl class="record" dir="${dir}" lang="${state.lang}">${rest.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
      ${att ? `<h3>${esc(t("attachments"))}</h3><ul class="docs-list">${att}</ul>` : ""}
      <details class="tech"><summary>${esc(t("tech"))}</summary>${factsList([
        [f.file, `<bdi class="code">${esc(s.file)}</bdi>`], [f.entry, `<bdi>${s.entry}</bdi>`], [f.version, esc(t("version")[s.lang])],
        [f.id, `<bdi>${esc(r.id)}</bdi>`], [f.field, `<bdi>${esc(state.field || "–")}</bdi>`], [f.updated, `<bdi>${esc(r.last_update || "–")}</bdi>`]])}
      ${state.trace ? `<p class="trace-title">${esc(t("trace_title"))}</p><pre dir="ltr" lang="en">${esc(JSON.stringify(state.trace, null, 1))}</pre>` : ""}</details>`;
  } catch (e) {
    $("#ev-body").innerHTML = `<p class="note warn">${esc(e.message)}</p>`;
  }
}

async function showDocument(state) {
  $("#ev-kind").textContent = t("loading");
  $("#ev-title").textContent = t("loading");
  $("#ev-body").innerHTML = "";
  try {
    const d = await cached(`/api/documents/${state.id}`);
    if (evidenceState !== state) return;
    const label = d.labels[0] || d.names[0].split("/").pop();
    const f = t("facts");
    $("#ev-kind").textContent = t("doc_kind")[d.kind] || d.kind;
    $("#ev-title").textContent = label;
    $("#ev-title").setAttribute("dir", dirOf(label));
    state.page = Math.min(Math.max(state.page || 1, 1), d.pages || 1);
    state.tab = state.tab || "page";
    const copies = d.names.length > 1 ? `<details class="copies"><summary>${esc(t("copies", d.names.length - 1))}</summary><bdi class="code">${d.names.slice(1).map(esc).join("<br>")}</bdi></details>` : "";
    $("#ev-body").innerHTML = `
      <div class="pager">
        <div class="tabs" role="tablist">
          <button type="button" role="tab" data-tab="page" aria-selected="${state.tab === "page"}">${esc(t("tab_page"))}</button>
          <button type="button" role="tab" data-tab="text" aria-selected="${state.tab === "text"}">${esc(t("tab_text"))}</button>
        </div>
        <div class="steps" dir="ltr">
          <button type="button" class="icon-btn" data-step="-1" aria-label="${esc(t("prev"))}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg></button>
          <span id="page-no"></span>
          <button type="button" class="icon-btn" data-step="1" aria-label="${esc(t("next"))}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></button>
        </div>
      </div>
      <p class="note warn" id="ocr-note" hidden>${esc(t("ocr_warn"))}</p>
      <div class="sheet-page" id="page-img-wrap"><img id="page-img" alt=""></div>
      <div class="page-text" id="page-text" hidden></div>
      <p class="download"><a href="/api/documents/${esc(state.id)}/original" download>${esc(t("download"))}</a></p>
      <details class="tech"><summary>${esc(t("tech"))}</summary>${factsList([
        [f.original, `<bdi class="code">${esc(d.names[0])}</bdi>${copies}`], [f.pages, `<bdi>${d.pages}</bdi>`],
        [f.text, esc(d.ocr_pages ? t("ocr_text", d.ocr_pages, d.pages) : t("text_layer"))],
        [f.sha, `<bdi class="code">${esc(d.sha256)}</bdi>`], [f.used_by, `<bdi>${d.procedures.length}</bdi>`]])}</details>`;
    const go = async (n) => {
      state.page = Math.min(Math.max(n, 1), d.pages || 1);
      $("#page-no").textContent = t("page_of", state.page, d.pages);
      $$("[data-step]").forEach((b) => { b.disabled = (b.dataset.step === "-1" && state.page <= 1) || (b.dataset.step === "1" && state.page >= d.pages); });
      $("#page-img").src = `/api/documents/${state.id}/pages/${state.page}/image`;
      $("#page-img").alt = `${label}, ${t("page_of", state.page, d.pages)}`;
      const p = await api(`/api/documents/${state.id}/pages/${state.page}`);
      if (evidenceState !== state) return;
      $("#ocr-note").hidden = p.method !== "ocr";
      const box = $("#page-text");
      box.setAttribute("dir", dirOf(p.text));
      box.innerHTML = highlight(p.text, state.terms || []);
    };
    const show = (tab) => {
      state.tab = tab;
      $$("[data-tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
      $("#page-img-wrap").hidden = tab !== "page";
      $("#page-text").hidden = tab !== "text";
    };
    $$("[data-step]").forEach((b) => b.addEventListener("click", () => go(state.page + Number(b.dataset.step))));
    $$("[data-tab]").forEach((b) => b.addEventListener("click", () => show(b.dataset.tab)));
    show(state.tab);
    await go(state.page);
  } catch (e) {
    $("#ev-body").innerHTML = `<p class="note warn">${esc(e.message)}</p>`;
  }
}

function opener(e) {
  const b = e.target.closest("[data-open]");
  if (!b) return false;
  e.preventDefault();
  $$(".source.active, .doc.active, .twin.active").forEach((x) => x.classList.remove("active"));
  b.classList.add("active");
  const ex = exchanges[Number(b.closest(".exchange")?.dataset.index)];
  const a = ex?.answer;
  const trace = a ? { field: a.intent, confidence: a.intent_confidence, masked: a.masked, claims: a.claims, ...a.trace } : null;
  if (b.dataset.open === "record") openEvidence({ kind: "record", entry: b.dataset.entry, lang: b.dataset.lang, field: b.dataset.field, trace });
  if (b.dataset.open === "doc") openEvidence({ kind: "doc", id: b.dataset.id, page: Number(b.dataset.page || 1), terms: (b.dataset.terms || "").split(" ").filter(Boolean) });
  return true;
}

function conflictRow(c, titles) {
  return `<li class="conflict"><p class="conflict-title" ${langAttrs(titles[c.key])}>${esc(titles[c.key] || c.key)}</p>
    <div class="twins small">
      <button type="button" class="twin" data-open="record" data-entry="${c.ar_ref.entry}" data-lang="ar" data-field="${esc(c.ar_ref.field)}" lang="ar" dir="rtl"><span class="twin-lang">العربية</span><span class="twin-value">${esc(c.ar)}</span></button>
      <button type="button" class="twin" data-open="record" data-entry="${c.fr_ref.entry}" data-lang="fr" data-field="${esc(c.fr_ref.field)}" lang="fr" dir="ltr"><span class="twin-lang">Français</span><span class="twin-value">${esc(c.fr)}</span></button>
    </div></li>`;
}

function docFinding(d) {
  const label = d.labels[0] || d.names[0].split("/").pop();
  return `<li><button type="button" class="doc" data-open="doc" data-id="${esc(d.id)}" data-page="1">${DOC_ICON}<span class="doc-name" ${langAttrs(label)}>${esc(label)}</span><span class="doc-meta">${esc(t("times", d.names.length))}</span></button></li>`;
}

async function loadInstitutions() {
  const [q, lib, g] = await Promise.all([cached("/api/quality"), cached("/api/library"), cached("/api/governance")]);
  const titles = q.titles || {};
  const copies = [...lib.list].sort((a, b) => b.names.length - a.names.length).slice(0, 4);
  const finding = (n, text, more) => `<li class="finding"><p class="figure"><bdi>${n}</bdi></p><div class="finding-body"><p>${esc(text)}</p>${more ? `<details><summary>${esc(t("examples_label"))}</summary>${more}</details>` : ""}</div></li>`;
  $("#findings").innerHTML = [
    finding(q.procedures_with_confirmed_conflict, t("f_conflict", q), `<ul class="conflicts">${q.conflicts.slice(0, 5).map((c) => conflictRow(c, titles)).join("")}</ul>`),
    finding(q.no_legal_basis, t("f_basis", q)),
    finding(lib.attachments, t("f_docs", lib), `<ul class="docs-list">${copies.map(docFinding).join("")}</ul>${lib.broken.length ? `<p class="small"><bdi class="code">${lib.broken.map((b) => esc(b.name)).join("<br>")}</bdi></p>` : ""}`),
    finding(q.duplicate_titles.length, t("f_dups"), `<ul class="plain-list">${q.duplicate_titles.map((x) => `<li ${langAttrs(titles[x[0]])}>${esc(titles[x[0]] || x[0])}</li>`).join("")}</ul>`),
  ].join("");
  if (!lastRun) {
    $("#stage-list").innerHTML = g.stages.map((s) => `<li class="stage"><p class="stage-head"><span class="stage-day">${esc(t("day", s.day))}</span><span class="stage-title">${esc(t("stage_titles")[s.id] || s.title)}</span></p><p class="stage-text" lang="en" dir="ltr">${esc(s.simulated)}</p></li>`).join("");
  }
  $("#gaps").innerHTML = g.gaps.map((x) => `<details class="gap"><summary><span class="gap-id">${esc(x.id)}</span><span class="gap-title" lang="en" dir="ltr">${esc(x.title)}</span><span class="tag">${esc(t("gap_type")[x.type] || x.type)}</span></summary>
    <dl lang="en" dir="ltr">
      <dt>${esc(t("g").evidence)}</dt><dd>${esc(x.evidence)}</dd>
      <dt>${esc(t("g").proposal)}</dt><dd>${esc(x.proposal)}</dd>
      <dt>${esc(t("g").example)}</dt><dd>${esc(x.global_example)}</dd>
      <dt>${esc(t("g").readiness)}</dt><dd>${x.readiness.map((d) => esc(`${d}. ${g.dimensions[d] || ""}`)).join("; ")}</dd>
    </dl></details>`).join("");
  $("#pipeline").innerHTML = t("pipeline").map(([n, c]) => `<dt dir="ltr">${esc(n)}</dt><dd>${esc(c)}</dd>`).join("");
}

function verdictClass(status) {
  return status === "ALLOWED" ? "ok" : status === "AWAITING_HUMAN" ? "wait" : "stop";
}

function renderRun(r) {
  const actions = r.stages.flatMap((s) => s.board.flatMap((b) => b.actions));
  const blocked = actions.filter((x) => x.status.startsWith("BLOCKED")).length;
  const human = actions.filter((x) => x.status === "AWAITING_HUMAN").length;
  const stages = r.stages.map((s) => {
    const acts = s.board.flatMap((b) => b.actions.map((x) => ({ ...x, agent: b.agent })));
    const count = (st) => s.answers.filter((a) => a.status === st).length;
    const sum = t("stage_sum", count("answered"), count("held"), count("refused"), acts.filter((x) => x.status.startsWith("BLOCKED")).length, acts.filter((x) => x.status === "AWAITING_HUMAN").length);
    const citizens = s.answers.map((a) => `<li><span class="badge ${a.status}">${esc(t(a.status))}</span><span ${langAttrs(a.query)}>${esc(a.query)}</span></li>`).join("");
    const decisions = acts.map((x) => `<li class="decision ${verdictClass(x.status)}"><span class="verdict">${esc(t("v")[x.status] || x.status)}</span><span><b>${esc(t("agents")[x.agent] || x.agent)}</b> ${esc(t("acts")[x.action] || x.action)}${x.status.startsWith("BLOCKED") ? `<span class="why" dir="ltr" lang="en">${esc(x.rule)}</span>` : ""}</span></li>`).join("");
    return `<li class="stage done"><details><summary><span class="stage-head"><span class="stage-day">${esc(s.stage.id)}</span><span class="stage-title">${esc(t("stage_titles")[s.stage.id] || s.stage.title)}</span></span><span class="stage-sum">${esc(sum)}</span></summary>
      <p class="stage-text" lang="en" dir="ltr">${esc(s.stage.simulated)}</p><ul class="citizens">${citizens}</ul><ul class="decisions">${decisions}</ul></details></li>`;
  }).join("");
  return `<div class="run-result"><p class="run-summary">${esc(t("summary", r.stages.length, blocked, human))}</p><p class="seal"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>${esc(t("ledger", r))}</p><ol class="stages">${stages}</ol></div>`;
}

async function runExercise(withEvent) {
  const status = $("#run-status");
  const buttons = $$("#inject-form button, #run-all");
  buttons.forEach((b) => { b.disabled = true; });
  const started = Date.now();
  status.textContent = t("running", 0);
  const timer = setInterval(() => { status.textContent = t("running", Math.round((Date.now() - started) / 1000)); }, 1000);
  try {
    const body = { use_llm: $("#use-llm").checked };
    if (withEvent) {
      body.inject = $("#inject").value.trim();
      body.inject_question = $("#inject-q").value.trim();
      body.stages = ["S1"];
    }
    lastRun = await api("/api/exercise", body);
    status.textContent = "";
    $("#stage-list").innerHTML = "";
    $("#run-output").innerHTML = renderRun(lastRun);
  } catch (e) {
    status.textContent = `${t("error")} ${e.message}`;
  } finally {
    clearInterval(timer);
    buttons.forEach((b) => { b.disabled = false; });
  }
}

function grow(el) {
  el.style.height = "auto";
  el.style.height = `${Math.min(el.scrollHeight + 2, 160)}px`;
}

function init() {
  $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
  $$(".views [data-view]").forEach((b) => b.addEventListener("click", () => setView(b.dataset.view)));
  const q = $("#q");
  $("#ask-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = q.value.trim();
    $("#q-error").textContent = text ? "" : t("empty_q");
    if (!text) { q.focus(); return; }
    q.value = "";
    grow(q);
    ask(text);
  });
  q.addEventListener("input", () => grow(q));
  q.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("#ask-form").requestSubmit(); } });
  document.addEventListener("click", (e) => {
    if (opener(e)) return;
    const example = e.target.closest(".example");
    if (example) { ask(example.textContent); return; }
    const pick = e.target.closest(".pick");
    if (pick) { ask(`${exchanges[Number(pick.dataset.index)].question} (${pick.dataset.title})`); return; }
    const retry = e.target.closest(".retry");
    if (retry) ask(exchanges[Number(retry.dataset.index)].question, Number(retry.dataset.index));
  });
  $("#reset").addEventListener("click", () => { exchanges.length = 0; renderThread(); closeEvidence(); q.focus(); });
  $("#ev-close").addEventListener("click", closeEvidence);
  $("#scrim").addEventListener("click", closeEvidence);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && evidenceState) closeEvidence(); });
  $("#run-all").addEventListener("click", () => runExercise(false));
  $("#inject-form").addEventListener("submit", (e) => { e.preventDefault(); if ($("#inject").value.trim()) runExercise(true); else $("#inject").focus(); });
  setLang(pickLanguage());
  setView("ask");
  api("/api/health").then((h) => { health = h; $("#health").textContent = t("health", h); }).catch(() => {});
}

init();
