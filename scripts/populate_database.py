#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
"""
import os
import sys
from datetime import datetime, timedelta
import random
import uuid
import json

# Mesma senha para todos (hash bcrypt de "senha123")
PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYmQzn6JC6W"

def load_env():
    """Carregar variáveis de ambiente do .env"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def populate_database():
    load_env()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    try:
        import psycopg
        from psycopg.rows import dict_row
        
        print("🚀 Populando Banco de Dados")
        print("=" * 60)
        
        conn = psycopg.connect(database_url, connect_timeout=10, row_factory=dict_row)
        cur = conn.cursor()
        
        # Verificar se já existem dados
        cur.execute("SELECT COUNT(*) as count FROM users WHERE email LIKE '%@example.com'")
        existing_users = cur.fetchone()['count']
        
        if existing_users > 0:
            print(f"\n⚠️  ATENÇÃO: Já existem {existing_users} usuários de exemplo no banco!")
            response = input("Deseja continuar e adicionar mais dados? (s/n): ")
            if response.lower() != 's':
                print("❌ Operação cancelada pelo usuário.")
                cur.close()
                conn.close()
                return False
        
        # 1. CRIAR USUÁRIOS
        print("\n👥 Criando usuários...")
        users_data = [
            ("João Silva", "joao@example.com", "+244 923 456 789", "Entusiasta de turismo e aventura em Angola", "tourist"),
            ("Maria Santos", "maria@example.com", "+244 923 456 790", "Apaixonada por praias e natureza", "tourist"),
            ("Pedro Costa", "pedro@example.com", "+244 923 456 791", "Fotógrafo de viagens", "tourist"),
            ("Ana Fernandes", "ana@example.com", "+244 923 456 792", "Guia turística profissional", "operator"),
            ("Carlos Mendes", "carlos@example.com", "+244 923 456 793", "Historiador e explorador cultural", "tourist"),
            ("Sofia Rodrigues", "sofia@example.com", "+244 923 456 794", "Blogger de viagens", "tourist"),
            ("Admin Wenda", "admin@wenda.ao", "+244 923 000 000", "Administrador do sistema Wenda", "admin"),
        ]
        
        user_ids = []
        for name, email, phone, bio, role in users_data:
            # Verificar se usuário já existe
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing = cur.fetchone()
            
            if existing:
                user_id = existing['id']
                print(f"  ⚠️  {name} ({email}) - já existe")
            else:
                user_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO users (id, name, email, password_hash, phone, bio, role, is_active, email_verified_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, true, CURRENT_TIMESTAMP)
                """, (user_id, name, email, PASSWORD_HASH, phone, bio, role))
                print(f"  ✓ {name} ({email})")
            
            user_ids.append(user_id)
        
        conn.commit()
        print(f"✅ {len(user_ids)} usuários criados!")
        
        # 2. OBTER CATEGORIAS
        print("\n🏷️  Obtendo categorias...")
        cur.execute("SELECT id, name, slug FROM categories ORDER BY display_order")
        categories = cur.fetchall()
        category_map = {cat['slug']: cat['id'] for cat in categories}
        print(f"✅ {len(categories)} categorias encontradas")
        
        # 3. CRIAR DESTINOS
        print("\n🏖️  Criando destinos turísticos...")
        destinations_data = [
            # LUANDA
            ("Fortaleza de São Miguel", "fortaleza-sao-miguel", "Fortaleza histórica do século XVI com vista para a baía de Luanda", 
             "A Fortaleza de São Miguel é um dos monumentos mais importantes de Angola, construída pelos portugueses em 1576. Hoje abriga o Museu das Forças Armadas.",
             "Luanda", "Luanda", "Rua Major Kanhangulo", category_map['historical'], -8.8137, 13.2343,
             "Terça a Domingo: 9h-17h", "500 Kz (adultos), 250 Kz (crianças)", "+244 222 334 455", "museu@fortaleza.ao", None,
             ["parking", "guide", "museum", "restroom"], ["wheelchair"], True),
            
            ("Ilha de Luanda", "ilha-luanda", "Península paradisíaca com praias de areia branca e vida noturna vibrante",
             "A Ilha do Cabo, conhecida como Ilha de Luanda, é um dos destinos mais populares da capital angolana. Oferece praias belíssimas, restaurantes de frutos do mar e uma vista espetacular do pôr do sol.",
             "Luanda", "Luanda", "Ilha de Luanda", category_map['natural'], -8.7832, 13.2000,
             "24 horas", "Gratuito", None, None, "https://ilha-luanda.ao",
             ["parking", "restaurant", "beach", "wifi"], ["beach_access"], True),
            
            ("Miradouro da Lua", "miradouro-lua", "Formações rochosas únicas esculpidas pela erosão, lembrando paisagem lunar",
             "O Miradouro da Lua é uma das maravilhas naturais de Angola, localizado a 40km de Luanda. As formações geológicas criadas pela erosão do vento e da chuva criam uma paisagem surreal.",
             "Luanda", "Luanda", "Estrada do Mussulo, Km 40", category_map['natural'], -9.0500, 13.0800,
             "24 horas", "Gratuito", None, None, None,
             ["parking", "viewpoint"], [], True),
            
            ("Mercado do Benfica", "mercado-benfica", "Mercado tradicional colorido com artesanato e cultura local",
             "O Mercado do Benfica é um dos mercados mais tradicionais de Luanda, onde é possível encontrar artesanato angolano, tecidos, frutas tropicais e experimentar a autêntica cultura local.",
             "Luanda", "Luanda", "Bairro do Benfica", category_map['cultural'], -8.8300, 13.2450,
             "Segunda a Sábado: 7h-19h", "Gratuito", None, None, None,
             ["parking", "market", "local_food"], [], False),
            
            # BENGUELA
            ("Praia Morena", "praia-morena", "Praia tranquila com águas cristalinas perfeita para relaxar",
             "A Praia Morena em Benguela é conhecida por suas águas calmas e areia dourada. É um local perfeito para famílias e para quem busca tranquilidade longe das multidões.",
             "Benguela", "Benguela", "Baía Farta", category_map['natural'], -12.5000, 13.1800,
             "24 horas", "Gratuito", None, None, None,
             ["parking", "beach", "restaurant"], ["beach_access"], True),
            
            ("Palácio da Praia Grande", "palacio-praia-grande", "Palácio colonial à beira-mar com arquitetura portuguesa",
             "O Palácio da Praia Grande é um edifício histórico localizado na orla de Benguela, representando a arquitetura colonial portuguesa. Atualmente serve como sede administrativa.",
             "Benguela", "Benguela", "Marginal de Benguela", category_map['historical'], -12.5763, 13.4055,
             "Segunda a Sexta: 8h-17h", "Gratuito", "+244 272 232 323", None, None,
             ["parking", "historic_building"], ["wheelchair"], False),
            
            # HUAMBO
            ("Cristo Rei do Huambo", "cristo-rei-huambo", "Estátua monumental do Cristo Rei com vista panorâmica da cidade",
             "A estátua do Cristo Rei no Huambo é um dos maiores monumentos religiosos de Angola, oferecendo uma vista panorâmica espetacular da cidade e do planalto central.",
             "Huambo", "Huambo", "Morro do Cristo Rei", category_map['cultural'], -12.7760, 15.7390,
             "24 horas", "Gratuito", None, None, None,
             ["parking", "viewpoint", "religious"], [], True),
            
            # NAMIBE
            ("Deserto do Namibe", "deserto-namibe", "Deserto costeiro com dunas gigantes e paisagens surreais",
             "O Deserto do Namibe é um dos desertos costeiros mais antigos do mundo. Suas dunas que encontram o mar criam paisagens únicas e inesquecíveis.",
             "Namibe", "Namibe", "Parque Nacional do Iona", category_map['natural'], -16.8667, 12.1500,
             "24 horas", "Entrada do parque: 2000 Kz", "+244 264 200 100", None, None,
             ["parking", "camping", "guide"], [], True),
            
            ("Fenda da Tundavala", "fenda-tundavala", "Mirante natural com vista de tirar o fôlego sobre o vale",
             "A Fenda da Tundavala é uma formação geológica espetacular com uma queda abrupta de mais de 1000 metros, oferecendo vistas panorâmicas de cortar a respiração.",
             "Namibe", "Lubango", "Serra da Leba", category_map['natural'], -14.9167, 13.5333,
             "24 horas", "500 Kz", None, None, None,
             ["parking", "viewpoint", "guide"], [], True),
            
            # HUÍLA
            ("Serra da Leba", "serra-leba", "Estrada sinuosa pelas montanhas com curvas espetaculares",
             "A Serra da Leba é famosa por sua estrada com curvas em zigue-zague, sendo um dos cartões postais de Angola. A vista do topo é simplesmente magnífica.",
             "Huíla", "Lubango", "EN280", category_map['natural'], -14.9500, 13.5500,
             "24 horas", "Gratuito", None, None, None,
             ["parking", "viewpoint", "scenic_drive"], [], True),
            
            # CUANDO CUBANGO
            ("Parque Nacional do Luengue-Luiana", "parque-luengue-luiana", "Santuário de vida selvagem com elefantes e leões",
             "O Parque Nacional do Luengue-Luiana faz parte do maior complexo de conservação transfronteiriço da África, abrigando uma rica diversidade de fauna.",
             "Cuando Cubango", "Menongue", "Região do Cuando Cubango", category_map['adventure'], -15.5000, 20.5000,
             "6h-18h", "3000 Kz + taxa de guia", "+244 249 200 200", None, None,
             ["camping", "safari", "guide", "wildlife"], [], False),
            
            # CABINDA
            ("Praia de Lândana", "praia-landana", "Praia isolada com coqueiros e águas mornas",
             "A Praia de Lândana em Cabinda é um paraíso tropical escondido, com coqueiros, areia branca e mar calmo. Perfeita para um retiro tranquilo.",
             "Cabinda", "Cabinda", "Lândana", category_map['natural'], -5.1833, 12.3167,
             "24 horas", "Gratuito", None, None, None,
             ["beach", "parking"], ["beach_access"], False),
        ]
        
        destination_ids = []
        for dest_data in destinations_data:
            # Verificar se destino já existe
            cur.execute("SELECT id FROM destinations WHERE slug = %s", (dest_data[1],))
            existing = cur.fetchone()
            
            if existing:
                dest_id = existing['id']
                print(f"  ⚠️  {dest_data[0]} ({dest_data[5]}) - já existe")
            else:
                dest_id = str(uuid.uuid4())
                # Converter amenities e accessibility para JSON
                amenities_json = json.dumps(dest_data[15])
                accessibility_json = json.dumps(dest_data[16])
                
                cur.execute("""
                    INSERT INTO destinations (
                        id, name, slug, description, long_description, location, province, address,
                        category_id, latitude, longitude, opening_hours, ticket_price, phone, email, website,
                        amenities, accessibility, is_featured
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (dest_id,) + dest_data[:15] + (amenities_json, accessibility_json, dest_data[17]))
                print(f"  ✓ {dest_data[0]} ({dest_data[5]})")
            
            destination_ids.append(dest_id)
        
        conn.commit()
        print(f"✅ {len(destination_ids)} destinos criados!")
        
        # 4. ADICIONAR IMAGENS AOS DESTINOS
        print("\n📸 Adicionando imagens aos destinos...")
        image_count = 0
        for dest_id in destination_ids:
            # 2-4 imagens por destino
            num_images = random.randint(2, 4)
            for i in range(num_images):
                cur.execute("""
                    INSERT INTO destination_images (destination_id, url, thumbnail_url, caption, is_main, display_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    dest_id,
                    f"https://picsum.photos/800/600?random={dest_id}{i}",
                    f"https://picsum.photos/400/300?random={dest_id}{i}",
                    f"Imagem {i+1}" if i > 0 else "Imagem principal",
                    i == 0,  # Primeira imagem é a principal
                    i
                ))
                image_count += 1
        
        conn.commit()
        print(f"✅ {image_count} imagens adicionadas!")
        
        # 5. CRIAR REVIEWS
        print("\n⭐ Criando avaliações...")
        review_comments = [
            "Lugar incrível! Recomendo muito a visita.",
            "Adorei! A vista é espetacular.",
            "Experiência maravilhosa, voltaria com certeza.",
            "Muito bom, mas pode melhorar a infraestrutura.",
            "Excelente destino para passar o dia com a família.",
            "Superou minhas expectativas!",
            "Lugar bonito mas estava muito cheio.",
            "Imperdível! Um dos melhores lugares de Angola.",
            "Ótimo para tirar fotos incríveis.",
            "Guias muito atenciosos e conhecedores.",
        ]
        
        review_count = 0
        for dest_id in destination_ids[:8]:  # Reviews nos primeiros 8 destinos
            # 2-5 reviews por destino
            num_reviews = random.randint(2, 5)
            reviewers = random.sample(user_ids[:6], min(num_reviews, 6))  # Não usar admin
            
            for user_id in reviewers:
                # Verificar se review já existe
                cur.execute("SELECT id FROM reviews WHERE user_id = %s AND destination_id = %s", (user_id, dest_id))
                if cur.fetchone():
                    continue
                
                rating = random.randint(3, 5)  # Ratings entre 3 e 5
                comment = random.choice(review_comments)
                
                cur.execute("""
                    INSERT INTO reviews (user_id, destination_id, rating, comment, is_verified)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, dest_id, rating, comment, random.choice([True, False])))
                
                review_id = cur.fetchone()['id']
                review_count += 1
                
                # Algumas reviews têm imagens
                if random.random() < 0.3:  # 30% das reviews têm imagens
                    cur.execute("""
                        INSERT INTO review_images (review_id, url, thumbnail_url)
                        VALUES (%s, %s, %s)
                    """, (
                        review_id,
                        f"https://picsum.photos/800/600?random=r{review_id}",
                        f"https://picsum.photos/400/300?random=r{review_id}"
                    ))
        
        conn.commit()
        print(f"✅ {review_count} avaliações criadas!")
        
        # 6. ADICIONAR HELPFUL VOTES
        print("\n👍 Adicionando votos 'útil' nas reviews...")
        cur.execute("SELECT id FROM reviews LIMIT 15")
        review_ids = [r['id'] for r in cur.fetchall()]
        
        helpful_count = 0
        for review_id in review_ids:
            # 1-4 usuários marcam como útil
            num_helpful = random.randint(1, 4)
            voters = random.sample(user_ids, num_helpful)
            
            for voter_id in voters:
                try:
                    cur.execute("""
                        INSERT INTO review_helpful (review_id, user_id)
                        VALUES (%s, %s)
                    """, (review_id, voter_id))
                    helpful_count += 1
                except:
                    pass  # Ignore duplicates
        
        conn.commit()
        print(f"✅ {helpful_count} votos adicionados!")
        
        # 7. CRIAR FAVORITOS
        print("\n❤️  Criando favoritos...")
        favorite_count = 0
        for user_id in user_ids[:5]:  # Primeiros 5 usuários
            # Cada usuário favorita 2-5 destinos
            num_favs = random.randint(2, 5)
            fav_dests = random.sample(destination_ids, num_favs)
            
            for dest_id in fav_dests:
                # Verificar se já existe
                cur.execute("SELECT user_id FROM favorites WHERE user_id = %s AND destination_id = %s", (user_id, dest_id))
                if cur.fetchone():
                    continue
                
                cur.execute("""
                    INSERT INTO favorites (user_id, destination_id)
                    VALUES (%s, %s)
                """, (user_id, dest_id))
                favorite_count += 1
        
        conn.commit()
        print(f"✅ {favorite_count} favoritos criados!")
        
        # 8. CRIAR VIAGENS
        print("\n🗺️  Criando viagens planejadas...")
        trip_names = [
            "Férias de Verão em Angola",
            "Tour Histórico",
            "Aventura no Deserto",
            "Praias do Sul",
            "Roteiro Cultural",
            "Escapada de Fim de Semana"
        ]
        
        trip_count = 0
        for i, user_id in enumerate(user_ids[:4]):  # Primeiros 4 usuários
            # 1-2 viagens por usuário
            for j in range(random.randint(1, 2)):
                start_date = datetime.now() + timedelta(days=random.randint(10, 90))
                end_date = start_date + timedelta(days=random.randint(3, 10))
                
                cur.execute("""
                    INSERT INTO trips (user_id, name, start_date, end_date, notes, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id,
                    random.choice(trip_names),
                    start_date.date(),
                    end_date.date(),
                    "Planejando uma viagem incrível por Angola!",
                    random.choice(['upcoming', 'upcoming', 'ongoing'])
                ))
                
                trip_id = cur.fetchone()['id']
                trip_count += 1
                
                # Adicionar 2-4 destinos à viagem
                num_dests = random.randint(2, 4)
                trip_dests = random.sample(destination_ids, num_dests)
                
                for order, dest_id in enumerate(trip_dests):
                    cur.execute("""
                        INSERT INTO trip_destinations (trip_id, destination_id, display_order, visit_date)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        trip_id,
                        dest_id,
                        order,
                        (start_date + timedelta(days=order)).date()
                    ))
        
        conn.commit()
        print(f"✅ {trip_count} viagens criadas!")
        
        # 9. CRIAR USER PREFERENCES
        print("\n⚙️  Criando preferências dos usuários...")
        for user_id in user_ids:
            # Verificar se já existe
            cur.execute("SELECT user_id FROM user_preferences WHERE user_id = %s", (user_id,))
            if cur.fetchone():
                continue
            
            # Categorias favoritas aleatórias
            fav_cats = random.sample(['natural', 'cultural', 'historical', 'adventure'], random.randint(1, 3))
            
            cur.execute("""
                INSERT INTO user_preferences (user_id, language, notifications_enabled, favorite_categories, theme)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                'pt',
                True,
                json.dumps(fav_cats),
                random.choice(['light', 'dark'])
            ))
        
        conn.commit()
        print(f"✅ {len(user_ids)} preferências criadas!")
        
        # RESUMO FINAL
        print("\n" + "=" * 60)
        print("🎉 BANCO DE DADOS POPULADO COM SUCESSO!")
        print("=" * 60)
        print(f"👥 Usuários:           {len(user_ids)}")
        print(f"🏖️  Destinos:          {len(destination_ids)}")
        print(f"📸 Imagens:           {image_count}")
        print(f"⭐ Avaliações:        {review_count}")
        print(f"👍 Votos 'útil':      {helpful_count}")
        print(f"❤️  Favoritos:         {favorite_count}")
        print(f"🗺️  Viagens:           {trip_count}")
        print(f"⚙️  Preferências:      {len(user_ids)}")
        print("=" * 60)
        print("\n📝 CREDENCIAIS DE LOGIN:")
        print("=" * 60)
        print("Email: joao@example.com")
        print("Email: maria@example.com")
        print("Email: pedro@example.com")
        print("Email: ana@example.com")
        print("Email: carlos@example.com")
        print("Email: sofia@example.com")
        print("Email: admin@wenda.ao (ADMIN)")
        print("\n🔑 Senha para todos: senha123")
        print("=" * 60)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = populate_database()
    sys.exit(0 if success else 1)
