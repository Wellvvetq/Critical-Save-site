import os
import json
from app import create_app
from app.services.db import get_db
from app.models import User, Game, Article, Career, StudioSetting

def seed():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # 1. Seed Initial Admin if none exists
        admin_user = db.session.query(User).filter_by(username="admin").first()
        if not admin_user:
            import secrets
            env_pwd = os.environ.get("INITIAL_ADMIN_PASSWORD")
            initial_password = env_pwd if env_pwd else secrets.token_urlsafe(16)
            admin_user = User(username="admin", role="admin")
            admin_user.set_password(initial_password)
            db.session.add(admin_user)
            if not env_pwd:
                print(f"[Seed] Generated secure initial admin credentials:")
                print(f"       Username: admin")
                print(f"       Password: {initial_password}")
            else:
                print(f"[Seed] Created admin account: 'admin' (password set from INITIAL_ADMIN_PASSWORD env)")

        # 2. Seed High-Quality Project Data (Honest, authentic studio project definitions)
        if db.session.query(Game).count() == 0:
            game1 = Game(
                slug="project-aegis-decay",
                title_en="Aegis Decay",
                tagline_en="A claustrophobic sci-fi survival narrative set in the decaying superstructure of an automated orbital foundry.",
                short_description_en="Trapped inside an unmonitored automated orbital refinery, an orbital engineer must navigate malfunctioning environmental regulators, cold mechanical logic, and decisions that permanently reconfigure the station's life support.",
                full_description_en="""Aegis Decay is an atmospheric first-person narrative survival experience built around genuine structural consequences.

When the station's automated maintenance protocol locks into quarantine, survival becomes an exercise in calculated triage. Every power redirect leaves another section frozen; every seal vented cuts off alternate routes. 

There are no superficial dialogue wheels: every progression decision is expressed directly through physical interaction with high-voltage industrial apparatus, station telemetry, and atmospheric pressure systems.""",
                genre_en="Sci-Fi / Narrative Survival",
                status_en="In Active Production",
                
                title_ru="Aegis Decay",
                tagline_ru="Клаустрофобный научно-фантастический выживательный нарратив в недрах угасающего орбитального завода.",
                short_description_ru="Оказавшись в ловушке на автоматизированном орбитальном комплексе, бортинженер сталкивается с логикой вышедших из строя протоколов и решениями, безвозвратно меняющими архитектуру систем жизнеобеспечения.",
                full_description_ru="""Aegis Decay — атмосферное нарративное выживание от первого лица, построенное на осязаемых последствиях принимаемых решений.

Когда протокол изоляции берет верх над станцией, выживание превращается в строгий инженерный расчет. Каждое перераспределение энергии лишает тепла другие секторы; каждый заблокированный шлюз навсегда отсекает пути отхода.

В игре нет декоративных диалоговых развилок: ключевые выборы осуществляются через физическое взаимодействие с промышленными телеметрическими консолями, клапанами давления и автоматикой станции.""",
                genre_ru="НФ / Нарративное выживание",
                status_ru="В активном производстве",
                
                cover_image="/static/images/aegis_cover.svg",
                hero_image="/static/images/aegis_hero.svg",
                trailer_url="https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
                gallery_images_json=json.dumps([
                    "/static/images/aegis_hero.svg",
                    "/static/images/aegis_cover.svg",
                    "/static/images/station_corridor.svg"
                ]),
                features_json_en=json.dumps([
                    "Persistent Station State: Subsystems stay damaged or powered according to your interventions.",
                    "Tactile Mechanical Interfaces: Direct interaction with realistic industrial switches, gauges, and telemetry.",
                    "Adaptive Soundscape: Acoustic propagation modeled directly through metallic station bulkheads and hollow airshafts.",
                    "Branching Survival Paths: No canonical route; manage dwindling resources according to your risk tolerance."
                ]),
                features_json_ru=json.dumps([
                    "Персистентное состояние станции: Системы остаются обесточенными или поврежденными в строгом соответствии с вашими действиями.",
                    "Тактильные приборные панели: Прямое взаимодействие с переключателями, аналоговыми манометрами и телеметрией.",
                    "Адаптивный акустический дизайн: Звук распространяется через металлические переборки и пустые вентиляционные шахты.",
                    "Ветвящиеся маршруты спасения: Отсутствие единственного пути; балансируйте между риском и дефицитом ресурсов."
                ]),
                platforms="PC (Steam / Windows)",
                release_date_info="TBA (Targeted 2027)",
                is_featured=True,
                is_published=True,
                sort_order=1
            )

            game2 = Game(
                slug="hollow-meridian",
                title_en="Hollow Meridian",
                tagline_en="An experimental investigative puzzle adventure across a fractured chronometer valley.",
                short_description_en="Step through an abandoned hydrological station in an alpine pass where local time fractures along electromagnetic fault lines.",
                full_description_en="""Hollow Meridian explores non-linear temporal investigation.

As an archivist dispatched to recover hydrological research records, you discover that the valley exists simultaneously across three distinct temporal states. Manipulating the flow of glacial runoff at the spillway causes immediate topological shifts across the past, present, and an unrecorded future.

Every puzzle challenges your spatial and causal perception, accompanied by a dynamic, evocative chamber-strings score.""",
                genre_en="Investigative / Puzzle",
                status_en="Pre-Production Prototype",
                
                title_ru="Hollow Meridian",
                tagline_ru="Экспериментальное исследовательское приключение с головоломками в долине временных разломов.",
                short_description_ru="Исследуйте заброшенную гидрологическую станцию в горном перевале, где локальное течение времени раскололось вдоль электромагнитных линий.",
                full_description_ru="""Hollow Meridian исследует нелинейное временное расследование.

В роли архивиста, направленного для сбора данных гляциологических наблюдений, вы обнаруживаете, что долина одновременно существует в трех временных состояниях. Управление потоками талой воды на водосбросе вызывает синхронные топологические сдвиги между прошлым, настоящим и будущим.

Каждая задача бросает вызов причинно-следственному восприятию под живой струнный саундтрек.""",
                genre_ru="Исследование / Головоломка",
                status_ru="Прототип пре-продакшна",
                
                cover_image="/static/images/meridian_cover.svg",
                hero_image="/static/images/meridian_hero.svg",
                trailer_url=None,
                gallery_images_json=json.dumps([
                    "/static/images/meridian_hero.svg",
                    "/static/images/meridian_cover.svg"
                ]),
                features_json_en=json.dumps([
                    "Tri-Temporal Mechanics: Shift mechanical devices across three synchronized eras to alter terrain.",
                    "Atmospheric Sound Architecture: Deep field recordings from sub-arctic permafrost zones.",
                    "Zero Hand-Holding: Clues and environmental causality are integrated seamlessly into the world design."
                ]),
                features_json_ru=json.dumps([
                    "Трихронная механика: Перемещение механизмов между эпохами для изменения рельефа местности.",
                    "Атмосферная звуковая архитектура: Натурные полевые записи из субарктических зон вечной мерзлоты.",
                    "Отсутствие искусственных подсказок: Все зацепки органично вплетены в архитектуру окружения."
                ]),
                platforms="PC",
                release_date_info="In Prototyping",
                is_featured=True,
                is_published=True,
                sort_order=2
            )

            db.session.add(game1)
            db.session.add(game2)
            print("[Seed] Seeded initial games.")

        # 3. Seed Articles
        if db.session.query(Article).count() == 0:
            a1 = Article(
                slug="manifesto-consequential-design",
                title_en="Engineering Agency: Why Critical Save Rejects Superficial Branching",
                excerpt_en="A technical and design breakdown of how we build systems where failure is a valid narrative state rather than a reload prompt.",
                content_en="""In contemporary game production, player agency is often reduced to ornamental branching: a dialogue tree with different emotional adjectives leading to the exact same cutscene, or a binary morality meter that adjusts an arbitrary ending slide.

At Critical Save Studio, we founded our design pipeline on the principle of the unbuffered consequence.

When an engineer in Aegis Decay chooses to overload a ventilation bypass to purge toxic gas from an access conduit, that conduit's thermal insulation is permanently vaporized. The adjacent cryo-storage unit loses refrigeration. Future navigation through that sector will require thermal insulation gear that could have been preserved for another tier.

We treat player actions not as narrative flags, but as physical state mutations. Failure is not a game-over screen requesting a reload; it is a permanent transformation of the simulation space that the player must live with.

Our goal is not to deliver dozens of shallow variations, but to make the path chosen feel earned, unyielding, and unforgettable.""",
                category_en="Design Philosophy",
                title_ru="Инженерия агентности: почему Critical Save отвергает декоративные развилки",
                excerpt_ru="Технический и геймдизайнерский разбор того, как мы строим системы, в которых неудача является полноценным нарративным состоянием, а не поводом для перезагрузки.",
                content_ru="""В современной игровой индустрии свобода выбора слишком часто сводится к декоративному ветвлению: реплики в диалогах с разными эмоциональными окрасками ведут в одну катсцену, а шкала кармы меняет лишь финальный слайд.

В Critical Save Studio мы выстроили наш подход на принципе неотменяемых последствий.

Когда игрок в Aegis Decay решает перегрузить байпас вентиляции для очистки перехода от ядовитого газа, термоизоляция секции испаряется безвозвратно. Соседний отсек криохранилища теряет охлаждение. Дальнейшее перемещение потребует теплозащиты, которую можно было сберечь для других систем.

Мы рассматриваем действия игрока не как флаги сценария, а как физические мутации состояния симуляции. Неудача — это не экран окончания игры с кнопкой повтора, а необратимая трансформация мира, с которой необходимо считаться.

Наша цель — не сотни поверхностных вариантов, а осязаемый, честный опыт каждого сделанного шага.""",
                category_ru="Философия дизайна",
                cover_image="/static/images/article_agency.svg",
                author="Lead Systems Designer",
                reading_time_minutes=4,
                is_published=True
            )

            a2 = Article(
                slug="acoustic-propagation-pipeline",
                title_en="Acoustic Spatialization: Modeling Pressure and Bulkhead Resonance",
                excerpt_en="Inside our audio rendering pipeline: creating dread through physics-based sound reflection instead of artificial jump scare stings.",
                content_en="""Atmosphere in horror and tension-focused experiences is won or lost in the frequency band below 200 Hz and the physical behavior of reverberation.

For our orbital environments, we developed an impulse-response workflow that calculates reflection based on material density — high-tensile steel, polycarbonate glass, and vacuum cavities. When a heavy valve releases pressure behind three closed bulkhead doors, the player hears neither a clear audio clip nor a generic muffled filter. Instead, the signal travels as mechanical vibration through the structural steel framing of the station floor before entering the air of the current compartment.

By respecting the physics of sound transmission, we build an organic sense of dread. The station feels alive, burdened, and mathematically indifferent to human vulnerability.""",
                category_en="Audio Engineering",
                title_ru="Акустическая пространственность: моделирование давления и резонанса переборок",
                excerpt_ru="Внутри нашего аудио-пайплайна: создание напряжения через физическое отражение звука вместо искусственных резких скримеров.",
                content_ru="""Атмосфера в играх напряжения формируется в диапазоне ниже 200 Гц и в физике затухания реверберации.

Для орбитальных локаций мы разработали систему импульсного отклика, вычисляющую отражения на основе плотности материалов — легированной стали, композитного стекла и вакуумных полостей. Когда тяжелый клапан сбрасывает давление за тремя закрытыми гермодверями, звук передается как механическая вибрация через металлоконструкции палубы.

Опираясь на физику звукопередачи, мы создаем неподдельное ощущение саспенса. Станция ощущается массивной, осязаемой и равнодушной к присутствию человека.""",
                category_ru="Аудио-инженерия",
                cover_image="/static/images/article_sound.svg",
                author="Audio Technical Lead",
                reading_time_minutes=5,
                is_published=True
            )

            db.session.add(a1)
            db.session.add(a2)
            print("[Seed] Seeded initial articles.")

        # 4. Seed Honest Careers
        if db.session.query(Career).count() == 0:
            c1 = Career(
                slug="senior-gameplay-systems-engineer",
                title_en="Senior Gameplay Systems Engineer (C++ / Physics)",
                department_en="Core Engineering",
                location_en="Remote (EU / CIS / Global) or Hybrid",
                description_en="We are looking for a Senior Gameplay Systems Engineer to spearhead our tactile mechanical interaction systems and persistent state architecture.",
                requirements_en="""- 5+ years of experience in real-time gameplay engineering.
- Deep proficiency in modern C++ and memory-conscious architectures.
- Experience building interactive mechanical rigs, physics constraints, and deterministic simulations.
- Passion for atmospheric, tension-driven game design.""",
                responsibilities_en="""- Architect reliable, modular physical interaction mechanics.
- Collaborate closely with narrative designers to implement non-reverting gameplay consequences.
- Profile and optimize CPU-bound physics routines across target PC hardware specifications.""",
                title_ru="Ведущий инженер игровых систем (C++ / Физика)",
                department_ru="Инженерия движка",
                location_ru="Удаленно или гибрид",
                description_ru="Мы ищем ведущего инженера для разработки систем тактильного механического взаимодействия и персистентного состояния мира.",
                requirements_ru="""- Опыт работы от 5 лет в разработке игровых механик в реальном времени.
- Глубокие знания современного C++ и архитектур с контролем памяти.
- Опыт создания физических сочленений, интерактивных механизмов и детерминированных симуляций.
- Любовь к атмосферным и напряженным игровым мирам.""",
                responsibilities_ru="""- Проектирование надежных модульных механик физического взаимодействия.
- Тесное взаимодействие с нарративной группой для реализации систем последствий.
- Профилирование и оптимизация вычислительных физических циклов под целевые конфигурации ПК.""",
                is_published=True
            )

            c2 = Career(
                slug="technical-lighting-artist",
                title_en="Technical Lighting & Environment Artist",
                department_en="Visual Art & Shading",
                location_en="Remote (Global)",
                description_en="Lead the lighting and atmosphere direction for our industrial sci-fi environments, balancing stark cinematic contrast with performant real-time rasterization.",
                requirements_en="""- Strong portfolio showcasing mastery over stark chiaroscuro lighting, volume acoustics, and atmospheric fog.
- Technical understanding of PBR shading models, radiance transfer, and performance budgeting.
- Eye for architectural scale, industrial authenticity, and mood.""",
                responsibilities_en="""- Author real-time lighting scenarios for claustrophobic interiors and planetary vistas.
- Optimize lighting shaders, shadow cascades, and volumetric caches for high framerates.
- Define art-directed visual boundaries that guide player navigation without UI markers.""",
                title_ru="Технический художник по свету и окружению",
                department_ru="Арт и шейдинг",
                location_ru="Удаленно",
                description_ru="Руководство направлением света и атмосферы для индустриальных интерьеров, баланс контраста и высокой производительности.",
                requirements_ru="""- Сильное портфолио с примерами контрастного светотеневого рисунка (кьяроскуро) и объемного тумана.
- Понимание принципов PBR-шейдеров, распространения света и оптимизации ресурсов рендера.
- Внимание к архитектурному масштабу, индустриальной достоверности и композиции.""",
                responsibilities_ru="""- Настройка световых сценариев для интерьеров и внешних панорам.
- Оптимизация шейдеров света, каскадов теней и объемных буферов для стабильного фреймрейта.
- Формирование визуальных ориентиров, направляющих игрока без навязчивого интерфейса.""",
                is_published=True
            )

            db.session.add(c1)
            db.session.add(c2)
            print("[Seed] Seeded initial career listings.")

        db.session.commit()
        print("[Seed] Database seed completed successfully.")

if __name__ == "__main__":
    seed()
