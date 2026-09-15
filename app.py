"""
Casa Oliva - Backend Flask + SQLite (arquivo unico)

Um unico arquivo, sem ORM: cria o banco, popula os 150 produtos na
primeira execucao e expoe a API que o front-end (templates/static) consome.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "casa_oliva.sqlite3"

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Dados do cardapio: (id, nome, descricao, preco, categoria, imagem)
# ---------------------------------------------------------------------------
PRODUTOS_SEED = [
    (1, 'Bruschetta al Pomodoro e Basilico', 'Pão rústico de fermentação natural tostado no azeite extravirgem, tomates concassé marinados, alho confit e manjericão fresco.', 38.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?auto=format&fit=crop&w=800&q=80'),
    (2, 'Carpaccio Clássico di Manzo', 'Finas lâminas de filé mignon curado, molho de alcaparras, mostarda dijon, lascas generosas de grana padano e rúcula precoce.', 56.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (3, 'Burrata Cremosa com Pesto Genovês', 'Burrata artesanal com recheio cremoso, telha crocante de focaccia, tomatinhos confitados e redução suave de aceto balsâmico.', 64.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1592417817098-8f3d6910985b?auto=format&fit=crop&w=800&q=80'),
    (4, 'Arancini de Funghi Porcini e Trufas', 'Croquetes sicilianos de risoto com cogumelos nobres, recheados com muçarela fior di latte e perfume de trufas negras.', 44.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80'),
    (5, 'Polvo Grelhado com Batatas Rústicas', 'Tentáculo de polvo selado na brasa, emulsão de páprica defumada, mini batatas ao murro e flor de sal de Guérande.', 78.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80'),
    (6, 'Steak Tartare do Chef', 'Filé mignon cortado na ponta da faca, gema caipira curada, echalotas, alcaparras e crocantes chips de batata doce.', 58.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=800&q=80'),
    (7, 'Vieiras Douradas na Manteiga de Ervas', 'Vieiras canadenses seladas ao ponto perfeito, mousseline de couve-flor trufada e telha de presunto cru.', 82.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80'),
    (8, 'Ceviche Peruano de Robalo', 'Cubos de robalo fresco marinados no leche de tigre cítrico, cebolla morada, milho chulpi crocante e coentro.', 52.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1535400255456-984241443b29?auto=format&fit=crop&w=800&q=80'),
    (9, 'Dadinhos de Tapioca com Geléia de Pimenta', 'Dadinhos dourados de queijo coalho e tapioca crocante por fora e macia por dentro, servidos com geléia artesanal.', 36.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80'),
    (10, 'Camarões Crocantes em Crosta de Panko', 'Camarões rosa empanados em farinha panko japonesa com aioli de limão siciliano e raspas de bottarga.', 68.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1559742811-822873691df8?auto=format&fit=crop&w=800&q=80'),
    (11, 'Tábua Rústica de Queijos e Embutidos', 'Seleção de queijo gorgonzola dolce, canastra curado, presunto parma 18 meses, salame milano e mel trufado.', 86.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80'),
    (12, 'Focaccia Genovese com Alecrim e Flor de Sal', 'Massa fofa e aromática assada no forno a lenha, regada com azeite toscano, alecrim selvagem e azeitonas pretas.', 32.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80'),
    (13, 'Croquete de Jamón Ibérico', 'Recheio bechamel ultracremoso com presunto pata negra curado, frito até dourar e servido bem quente.', 42.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80'),
    (14, 'Salada Caprese Contemporânea', 'Tomates heirloom coloridos, bocconcini de búfala, azeite de manjericão roxo e telhas crocantes de sementes.', 46.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1592417817098-8f3d6910985b?auto=format&fit=crop&w=800&q=80'),
    (15, 'Caldinho de Frutos do Mar Perfumado', 'Fundo rico de lagostins, peixe branco e mexilhões com leite de coco suave, capim-santo e croutons dourados.', 39.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80'),
    (16, 'Pastel de Brie com Geleia de Figo', 'Massa fininha e crocante recheada com queijo brie derretido, acompanhada de compota artesanal de figos turcos.', 38.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1608897013039-887f21d8c804?auto=format&fit=crop&w=800&q=80'),
    (17, 'Cogumelos Salteados na Manteiga de Sálvia', 'Mix de shimeji, shitake e portobello salteados com vinho branco, sálvia fresca e torradinhas rústicas.', 48.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80'),
    (18, 'Tartar de Salmão com Avocado', 'Salmão fresco picado na faca com avocado maduro, gergelim tostado, molho ponzu cítrico e chips de nori.', 54.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'),
    (19, 'Crostini de Queijo de Cabra e Mel', 'Fatias de baguete artesanal tostadas com chèvre cremoso gratinado, nozes douradas e fio de mel silvestre.', 41.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80'),
    (20, 'Lula Dourada à Dorê com Molho Tártaro', 'Anéis de lula tenros empanados levemente com fécula e especiarias, servidos com molho tártaro artesanal.', 59.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80'),
    (21, 'Mini Empanadas Criollas Argentinas', 'Massa amanteigada assada recheada com carne nobre marinada, ovos, azeitonas e cominho com chimichurri fresco.', 35.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1628294895950-9805252327bc?auto=format&fit=crop&w=800&q=80'),
    (22, 'Pimentões Padrón Chamuscados', 'Pimentões espanhóis fritos no azeite quente até tostarem levemente, finalizados com flor de sal crocante.', 34.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80'),
    (23, 'Carpaccio de Salmão com Alcaparras e Dill', "Fatias translúcidas de salmão norueguês fresco, emulsão de mostarda l'ancienne e folhas viçosas de endro.", 62.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80'),
    (24, 'Polenta Cremosa com Ragu de Ossobuco', 'Polenta italiana mole com queijo pecorino, coroada por ragu cozido lentamente por 12 horas ao vinho tinto.', 47.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1543339308-43e59d6b73a6?auto=format&fit=crop&w=800&q=80'),
    (25, 'Ceviche Misto de Frutos do Mar', 'Robalo, camarão e lula marinados com pimenta dedo-de-moça, cebola roxa, batata doce glaceada e coentro.', 66.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1535400255456-984241443b29?auto=format&fit=crop&w=800&q=80'),
    (26, 'Tartar de Atum com Crocante de Wonton', 'Atum fresco yellowfin com toques de óleo de gergelim, cebolinha, gengibre e telhas crocantes de wonton.', 61.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80'),
    (27, 'Queijo Brie En Croute com Amêndoas', 'Brie envolto em massa folhada folhada dourada, assado até amolecer por completo, com calda de frutas vermelhas.', 55.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1505253758473-96b3d55fdd6f?auto=format&fit=crop&w=800&q=80'),
    (28, 'Mexilhões à provençal com Tomates e Ervas', 'Mexilhões frescos salteados com vinho branco seco, alho dourado, tomate pelado e salsinha fresca picada.', 53.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80'),
    (29, 'Sopa Fria Gazpacho Andaluz', 'Clássico refrescante espanhol feito com tomates maduros, pepino, pimentão vermelho, azeite e croutons caseiros.', 33.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80'),
    (30, 'Vol-au-vent de Camarão com Catupiry', 'Folhado leve e crocante recheado com camarões médios salteados em creme sedoso de queijo requeijão artesanal.', 49.0, 'ENTRADAS', 'https://images.unsplash.com/photo-1559742811-822873691df8?auto=format&fit=crop&w=800&q=80'),
    (31, 'Bife de Chorizo Black Angus 350g', 'Corte nobre grelhado na parrilha a carvão vegetal, servido com chimichurri fresco e legumes assados no azeite.', 118.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80'),
    (32, 'Tornedor de Filé Mignon ao Poivre Vert', 'Medalhão alto envolvido em molho sedoso de pimenta verde fresca, conhaque e risoto cremoso de parmesão.', 108.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (33, 'Risoto de Camarões Rosa e Açafrão', 'Arroz carnaroli lentamente cozido com caldo artesanal de crustáceos, açafrão espanhol e camarões grelhados.', 98.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'),
    (34, 'Costela Bovina Cozida em Baixa Temperatura', 'Costela marinada e braseada por 24 horas, glaceada no demi-glace com purê aveludado de mandioquinha.', 96.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (35, 'Gnocchi Rústico de Batata com Ragu de Cordeiro', 'Nhoque artesanal de textura ultraleve selado na manteiga de tomilho, coberto por ragu encorpado de cordeiro.', 84.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80'),
    (36, 'Salmão Grelhado em Crosta de Ervas', 'Filé alto de salmão fresco selado ao ponto úmido, mousseline de batata baroa e legumes da horta glaceados.', 92.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80'),
    (37, 'Bacalhau Confitado à Moda do Lagar', 'Lombo nobre de bacalhau gadus morhua imerso em azeite extravirgem, alho assado, cebolas caramelizadas e batatas.', 128.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1535400255456-984241443b29?auto=format&fit=crop&w=800&q=80'),
    (38, 'Polvo à Lagareiro na Brasa', 'Tentáculos inteiros de polvo grelhados com azeite quente perfumado com alho laminado, brócolis ramoso e batata ao murro.', 124.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80'),
    (39, 'Tagliolini Artesanal com Frutos do Mar', 'Massa fresca da casa salteada com vôngoles, mexilhões, camarões, lulas frescas e emulsão leve de vinho branco.', 94.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80'),
    (40, 'Risoto de Cogumelos Selvagens e Trufa', 'Seleção de porcini, trufa negra, shimeji e portobello com manteiga noisette e queijo grana padano 24 meses.', 88.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=800&q=80'),
    (41, 'Paleta de Cordeiro Assada com Cuscuz Marroquino', 'Carne tenra desmanchando ao garfo com molho do próprio assado, hortelã fresca e cuscuz com amêndoas tostadas.', 114.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (42, 'Prime Rib Suíno Duroc com Chutney de Abacaxi', 'Corte suíno extremamente marmorizado grelhado ao ponto suculento, acompanhado de farofa de castanha e chutney.', 86.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (43, 'Pato Confitado ao Molho de Laranja e Grand Marnier', 'Coxa e sobrecoxa marinadas lentamente na própria gordura, pele super crocante e purê de batata trufado.', 106.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1514944298352-f47285d0d1e0?auto=format&fit=crop&w=800&q=80'),
    (44, 'Robalo em Crosta de Castanhas Brasileiras', 'Peixe nobre de carne branca com crosta dourada de castanhas-do-pará e caju, sobre cama de risoto de limão siciliano.', 99.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'),
    (45, 'Penne Rigate ao Pesto Cremoso com Burrata', 'Massa de grano duro cozida al dente com pesto fresco de manjericão, pinoli, tomatinhos tostados e burrata inteira.', 79.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1621996346565-e3d5d6281699?auto=format&fit=crop&w=800&q=80'),
    (46, 'Ossobuco alla Milanese com Risoto de Açafrão', 'Clássico italiano braseado ao vinho branco com mirepoix de legumes aromáticos e gremolata cítrica fresca.', 102.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (47, 'Moqueca Nobre de Peixe Branco e Camarões', 'Cozimento tradicional em panela de barro com pimentões, cebola, azeite de dendê balanceado, arroz e pirão leve.', 112.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1535400255456-984241443b29?auto=format&fit=crop&w=800&q=80'),
    (48, 'Ravioli de Abóbora com Amaretto e Manteiga de Sálvia', 'Massa fina recheada com abóbora kabocha assada, especiarias, amêndoas laminadas tostadas e queijo parmesão.', 76.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80'),
    (49, 'Ancho Grelhado com Aligot de Dois Queijos', '320g de corte alto de novilho precoce com aligot aveludado de queijo gruyère e meia cura, com redução de cabernet.', 116.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80'),
    (50, 'Atum Selado em Crosta de Gergelim Bicolor', 'Lombo de atum fresco com interior rosado e fresco, salteado de legumes orientais com molho tarê artesanal.', 95.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80'),
    (51, 'Lasagna Clássica alla Bolognese Gratinada', 'Camadas intercaladas de massa caseira, ragu de carne cozido por horas, bechamel acetinado e parmesão tostado.', 74.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?auto=format&fit=crop&w=800&q=80'),
    (52, 'Filé Oswaldo Aranha Especial', 'Filé mignon alto grelhado coberto por crocante alho frito dourado, batatas portuguesas estufadas, arroz e farofa de ovos.', 89.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (53, 'Risoto de Pera Caramelizada com Gorgonzola', 'Equilíbrio marcante entre a doçura da pera glaceada no vinho branco e o queijo gorgonzola dolce com nozes pecã.', 82.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=800&q=80'),
    (54, 'Galeto Primo Canto Desossado e Marinado', 'Galeto marinado na cerveja preta e ervas de provence, assado na brasa com polenta frita crocante e salada radicchio.', 69.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=800&q=80'),
    (55, 'Paella Valenciana de Carnes e Frutos do Mar', 'Arroz bomba espanhol com açafrão em estigmas, frango marinado, lula, mexilhões, camarões e ervilhas frescas.', 115.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'),
    (56, 'Stinco de Cordeiro Glaceado com Polenta Mole', 'Corte nobre da perna do cordeiro com osso, braseado em caldo denso de especiarias e vinho merlot.', 109.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (57, 'Espaguete Carbonara Tradizionale', 'Autêntica receita italiana com guanciale curado crocante, gemas pasteurizadas, pimenta-do-reino e queijo pecorino romano.', 78.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=800&q=80'),
    (58, 'Cavaquinha Grelhada na Manteiga de Garrafa', 'Lagostins brasileiros nobres grelhados na casca com ervas da horta, arroz com castanhas e vinagrete de manga.', 138.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1559742811-822873691df8?auto=format&fit=crop&w=800&q=80'),
    (59, 'Medalhões Suínos ao Molho de Mostarda e Mel', 'Filé mignon suíno tenro com molho aromático de mostarda antiga, legumes tostados no forno e batatas noisette.', 72.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
    (60, 'Risoto de Limão Cravo com Robalo Grelhado', 'Arroz cremoso finalizado com manteiga e raspas do limão cravo colhido no dia, coroado com posta grelhada de robalo.', 97.0, 'PRATO PRINCIPAL', 'https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80'),
    (61, 'Tiramisù Clássico Veneziano', 'Biscoitos savoiardi artesanais embebidos em café espresso forte e licor amaretto, creme denso de mascarpone e cacau 100%.', 36.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=800&q=80'),
    (62, 'Petit Gâteau Belge com Sorvete de Fava de Baunilha', 'Bolo quente de chocolate belga 70% com interior líquido e aveludado, servido com sorvete artesanal de baunilha de Madagascar.', 38.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80'),
    (63, 'Panna Cotta com Coulis de Frutas Vermelhas', 'Creme de leite fresco aromatizado com fava de baunilha, textura sedosa e calda ácida de amoras, mirtilos e framboesas.', 32.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80'),
    (64, 'Mil-Folhas Crocante com Creme Patissière', 'Camadas ultrafinas e estaladiças de massa folhada caramelizada intercaladas com creme de confeiteiro e açúcar de confeiteiro.', 35.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80'),
    (65, 'Cheesecake Nova-Iorquino com Calda de Goiabada Cascão', 'Base amanteigada crocante com recheio denso e aveludado de cream cheese, coberto por calda rústica de goiaba artesanal.', 34.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80'),
    (66, 'Crème Brûlée com Crosta de Açúcar Queimado', 'Clássica sobremesa francesa à base de gemas e creme de leite fresco, coberta com casquinha crocante de caramelo feita na hora.', 33.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1470124182917-cc6e71b22ecc?auto=format&fit=crop&w=800&q=80'),
    (67, 'Cannoli Siciliani Recheados com Ricota e Pistache', 'Massa frita crocante aromatizada com vinho marsala, recheio leve de ricota fresca de ovelha, gotas de chocolate e pistache.', 32.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80'),
    (68, 'Torta Mousse de Três Chocolates', 'Composição harmoniosa de mousses de chocolate amargo 70%, chocolate ao leite cremoso e chocolate branco aerado.', 37.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'),
    (69, 'Pudim de Leite Fava de Baunilha sem Furinhos', 'Pudim ultracremoso e liso com textura aveludada, favas naturais de baunilha e calda dourada de caramelo brilhante.', 28.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1528975604071-b4dc52a2d18c?auto=format&fit=crop&w=800&q=80'),
    (70, 'Profiteroles com Sorvete e Calda Quente de Chocolate', 'Carolinas leves e aeradas recheadas com sorvete artesanal de creme, finalizadas à mesa com ganache quente de cacau.', 35.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80'),
    (71, 'Tarte Tatin Francesa de Maçãs Caramelizadas', 'Maçãs caramelizadas na manteiga e açúcar até dourarem intensamente, assadas sob massa folhada com sorvete de canela.', 36.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1519915028121-7d3463d20b13?auto=format&fit=crop&w=800&q=80'),
    (72, 'Cocada Cremosa de Forno com Sorvete de Tapioca', 'Feita com coco fresco ralado e leite condensado cozido até dourar, crocante na superfície e quente por dentro.', 31.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&w=800&q=80'),
    (73, 'Brownie Fudgy de Nozes Pecã com Calda Toffee', 'Massa densa e molhadinha de chocolate nobre com nozes crocantes, acompanhada de sorvete de caramelo salgado.', 34.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80'),
    (74, 'Pavlova de Frutas Tropicais Frescas', 'Base de merengue seco crocante por fora e marshmallow por dentro, chantilly de fava de baunilha, maracujá e morangos.', 35.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80'),
    (75, 'Sorvete Artesanal de Pistache Siciliano', 'Duas bolas de sorvete de textura ultracremosa feito com pasta pura de pistache de Bronte e pedacinhos crocantes.', 30.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80'),
    (76, 'Fondant Quente de Doce de Leite Viçosa', 'Bolo macio com recheio cremoso e escorrendo de autêntico doce de leite mineiro, servido com sorvete de queijo da serra.', 36.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80'),
    (77, 'Carpaccio de Abacaxi Grelhado com Raspas de Limão', 'Lâminas de abacaxi marinadas com açúcar mascavo e especiarias grelhadas na brasa, servidas com sorbet de hortelã.', 26.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=800&q=80'),
    (78, 'Churros Espanhóis com Doce de Leite e Nutella', 'Porção com quatro churros dourados passados no açúcar refinado e canela em pó, servidos com duas opções de mergulho.', 29.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1624353365286-3f8d62daad51?auto=format&fit=crop&w=800&q=80'),
    (79, 'Bolo Gelado de Coco Embrulhado no Alumínio', 'Massa fofinha de pão de ló super molhada em calda de leite condensado e leite de coco, coberta por flocos de coco.', 24.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'),
    (80, 'Torta Sablée de Limão Siciliano com Merengue Suíço', 'Massa crocante que derrete na boca, recheada com curd azedinho e perfumado de limão e merengue tostado com maçarico.', 33.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1519915028121-7d3463d20b13?auto=format&fit=crop&w=800&q=80'),
    (81, 'Gelato de Gianduia e Avelãs Tostadas', 'Sobremesa gelada italiana unindo o chocolate ao leite e a pasta de avelãs do Piemonte com crocante tostado.', 32.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80'),
    (82, 'Semifreddo de Amêndoas com Calda de Café', 'Sobremesa gelada de consistência aveludada com crocante de praliné de amêndoas e dose de café espresso quente.', 31.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80'),
    (83, 'Frutas Frescas da Estação Fatiadas', 'Prato elegante com lâminas de melão orange, mamão papaya, uvas sem semente, morangos e mirtilos frescos.', 22.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=800&q=80'),
    (84, 'Taça Affogato al Caffè com Biscoito Cantuccini', 'Uma bola generosa de sorvete de baunilha servida em taça de cristal regada com shot de espresso e cantuccini.', 25.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=800&q=80'),
    (85, 'Mousse Leve de Maracujá com Sementes Crocantes', 'Creme aerado e refrescante equilibrando a acidez do maracujá da caatinga com redução doce das sementes da fruta.', 25.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80'),
    (86, 'Torta de Maçã Quente da Vovó', 'Fatias finas de maçã assadas com manteiga, açúcar mascavo e noz-moscada dentro de crosta dourada e crocante.', 29.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1519915028121-7d3463d20b13?auto=format&fit=crop&w=800&q=80'),
    (87, 'Romeu e Julieta Quente de Forno', 'Queijo da canastra gratinado em cumbuca rústica com goiabada cascão borbulhante e torradinhas amanteigadas.', 28.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&w=800&q=80'),
    (88, 'Gelato de Chocolate Amargo 80% Zero Açúcar', 'Opção funcional e intensa preparada com cacau especial, adoçado naturalmente e com textura surpreendente.', 30.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?auto=format&fit=crop&w=800&q=80'),
    (89, 'Merengue Suíço com Morangos Frescos e Chantilly', 'Suspiros artesanais crocantes desmanchando na boca com chantilly caseiro leve e morangos frescos picados.', 28.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80'),
    (90, 'Brigadeiro Gourmet de Colher com Cacau Callebaut', 'Servido quente em panelinha de cobre com raspas de chocolate meio amargo e confeitos crocantes belgas.', 24.0, 'SOBREMESAS', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'),
    (91, 'Suco Natural de Laranja Fresca 400ml', 'Laranjas pera selecionadas espremidas na hora do pedido, servidas bem geladas sem adição de água.', 14.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80'),
    (92, 'Limonada Suíça Cremosa com Hortelã', 'Limão taiti batido com gelo, folhas frescas de hortelã e leite condensado para um toque aveludado e refrescante.', 16.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
    (93, 'Água Mineral San Pellegrino 500ml', 'Água mineral com gás natural importada da Itália, servida em garrafa de vidro com rodela de limão siciliano.', 19.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80'),
    (94, 'Água Mineral Acqua Panna sem Gás 500ml', 'Água pura das colinas toscanas da Itália, sabor neutro e equilibrado para harmonização gastronômica.', 19.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80'),
    (95, 'Água Mineral Nacional sem Gás 310ml', 'Água pura de nascente montanhosa servida em garrafa de vidro bem gelada.', 8.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80'),
    (96, 'Água Mineral Nacional com Gás 310ml', 'Água mineral gaseificada refrescante servida com gelo filtrado e fatia de limão taiti.', 8.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80'),
    (97, 'Refrigerante Coca-Cola Original Lata 350ml', 'Servida trincando de gelada com copo longo, rodelas de limão e cubos de gelo cristalino.', 9.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'),
    (98, 'Refrigerante Coca-Cola Sem Açúcar Lata 350ml', 'Refrescância sem calorias servida com gelo cristalino e fatia de limão.', 9.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'),
    (99, 'Refrigerante Guaraná Antarctica Lata 350ml', 'O autêntico sabor do fruto da Amazônia servido bem gelado.', 9.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'),
    (100, 'Refrigerante Guaraná Zero Lata 350ml', 'Sabor característico do guaraná sem calorias, servido com gelo e limão.', 9.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80'),
    (101, 'Chá Gelado Artesanal de Pêssego e Capim-Santo', 'Infusão natural de chá preto, purê artesanal de pêssego fresco e folhas aromáticas de capim-santo.', 15.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=800&q=80'),
    (102, 'Soda Italiana de Maçã Verde e Gengibre', 'Água gaseificada premium, xarope francês Monin de maçã verde e lâminas de gengibre fresco.', 18.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
    (103, 'Soda Italiana de Cranberry e Hibisco', 'Bebida leve e gaseificada com xarope artesanal de hibisco e cranberry com rodelas de laranja.', 18.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
    (104, 'Suco Verde Detox Antioxidante 400ml', 'Abacaxi, couve orgânica, gengibre, hortelã e água de coco natural batidos na hora.', 17.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80'),
    (105, 'Água de Coco Fresca da Bahia 300ml', 'Servida em copo alto diretamente do coco verde refrigerado.', 12.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80'),
    (106, 'Suco de Maracujá com Tangerina 400ml', 'Mistura vibrante e refrescante unindo a polpa natural de maracujá e tangerina ponkan.', 16.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80'),
    (107, 'Suco de Frutas Vermelhas com Água de Coco', 'Framboesa, amora e morango batidos levemente com água de coco natural gelada.', 18.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=800&q=80'),
    (108, 'Mocktail Tropical Sunset sem Álcool', 'Suco de manga, xarope de grenadine, suco de laranja e água com gás em degradê com alecrim.', 24.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
    (109, 'Café Espresso Seleção Especial do Cerrado', 'Grãos 100% arábica com notas de caramelo e chocolate, extraído na pressão ideal com crema densa.', 9.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80'),
    (110, 'Café Espresso Macchiato Italiano', 'Shot curto de espresso especial finalizado com uma colherada de espuma densa de leite vaporizado.', 11.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80'),
    (111, 'Cappuccino Tradicional Italiano com Canela', 'Proporção clássica de espresso, leite vaporizado aveludado e espuma espessa com raspas de chocolate.', 14.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&w=800&q=80'),
    (112, 'Chá Inglês Twinings Earl Grey Quente', 'Chá preto perfumado com óleo essencial de bergamota cítrica, servido em bule de porcelana com mel.', 12.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80'),
    (113, 'Cerveja Artesanal IPA 500ml', 'Cerveja lupulada com amargor marcante, notas florais e cítricas e teor alcoólico de 6,5%.', 28.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1608270104840-06eb8b16cb2c?auto=format&fit=crop&w=800&q=80'),
    (114, 'Cerveja Pilsen Premium Long Neck 355ml', 'Lager dourada clara, corpo leve e refrescante, perfeita para iniciar a refeição.', 16.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1608270104840-06eb8b16cb2c?auto=format&fit=crop&w=800&q=80'),
    (115, 'Cerveja Witbier Belga com Casca de Laranja e Coentro', 'Cerveja de trigo não filtrada, extremamente aromática, leve e refrescante.', 26.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1608270104840-06eb8b16cb2c?auto=format&fit=crop&w=800&q=80'),
    (116, 'Cerveja Sem Álcool Heineken 0.0 Long Neck 330ml', 'Puro malte equilibrada e com sabor marcante de lúpulo sem teor alcoólico.', 16.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1608270104840-06eb8b16cb2c?auto=format&fit=crop&w=800&q=80'),
    (117, 'Drink Aperol Spritz Casa Oliva', 'Aperol, espumante prosecco brut, água gaseificada e fatia de laranja bahia em taça bojuda com gelo.', 36.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1560512823-829485b8bf24?auto=format&fit=crop&w=800&q=80'),
    (118, 'Drink Negroni Clássico envelhecido', 'Gin London Dry, Campari bitter e vermute tinto doce equilibrados em partes iguais com casca de laranja.', 38.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80'),
    (119, 'Drink Gin & Tonic Botânico com Alecrim e Zimbro', 'Gin premium nacional, água tônica artesanal, bagas de zimbro esmagadas e ramo de alecrim tostado.', 39.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80'),
    (120, 'Drink Moscow Mule na Caneca de Cobre', 'Vodka destilada, suco de limão taiti fresco, xarope de gengibre e espuma aerada de gengibre com raspas de limão.', 37.0, 'BEBIDAS', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
    (121, 'Brunello di Montalcino DOCG Banfi (Toscana)', '100% Sangiovese Grosso estagiado em carvalho. Notas profundas de cereja madura, tabaco, couro e taninos nobres.', 490.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (122, 'Barolo DOCG Pio Cesare (Piemonte)', 'Casta Nebbiolo com aromas etéreos de rosas secas, trufas e especiarias doces, com final longo e vigoroso.', 560.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (123, 'Chianti Classico Riserva Castello di Ama', 'Elegante e equilibrado vinho toscano com fruta vermelha vibrante, notas balsâmicas e acidez gastronômica primorosa.', 280.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (124, 'Amarone della Valpolicella Sartori (Vêneto)', 'Produzido a partir de uvas passificadas com notas densas de ameixa seca, chocolate amargo e figos em calda.', 420.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (125, 'Châteauneuf-du-Pape Domaine du Vieux Télégraphe', 'Ícone do Vale do Rhône francês com corte de Grenache, Syrah e Mourvèdre. Especiarias finas e frutas negras.', 530.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (126, 'Bordeaux Grand Cru Saint-Émilion Château Angelus', 'Corte bordalês rico com Merlot predominante, toques de baunilha francesa, cedro e textura aveludada incomparável.', 890.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (127, 'Bourgogne Pinot Noir Domaine Faiveley', 'Pinot noir delicado da Borgonha francesa, com frescor mineral, framboesas silvestres e notas de chão de floresta.', 340.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (128, 'Malbec Catena Zapata Nicasia Vineyard (Mendoza)', 'Malbec de vinhedo único em grande altitude, cor púrpura intensa, amoras maduras, grafite e taninos doces.', 480.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (129, 'Cabernet Sauvignon Montes Alpha Special Cuvée (Colchagua)', 'Excelente exemplar chileno com notas marcantes de cassis, pimentão vermelho tostado e carvalho francês tostado.', 210.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (130, 'Carménère Carmín de Peumo Concha y Toro', 'Um dos maiores ícones da casta Carménère no mundo, camadas de frutas escuras, chocolate e café expresso.', 620.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (131, 'Rioja Gran Reserva Marqués de Riscal (Espanha)', 'Elaborado com Tempranillo antigo com longa guarda em barrica, notas de couro, baunilha e frutas em compota.', 310.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (132, 'Ribera del Duero Alión Grupo Vega Sicilia', 'Tinto espanhol moderno e potente, fruta exuberante, minerais escuros e carvalho novo de altíssima estirpe.', 580.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (133, 'Tinto Pesquera Crianza Alejandro Fernández', 'Vinho estruturado da Ribera del Duero com notas de cereja preta, tostados elegantes e final fresco prolongado.', 260.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (134, 'Douro Tinto Quinta do Crasto Reserva Vinhas Velhas', 'Corte de vinhas centenárias portuguesas com imensa concentração de aroma de esteva, amoras e taninos sedosos.', 360.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'),
    (135, 'Alentejo Cartuxa Reserva Tinto Évora', 'Clássico vinho alentejano com fruta madura, corpo aveludado e notas marcantes de especiarias e madeira nobre.', 320.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
    (136, 'Chablis Premier Cru Domaine Laroche (Borgonha)', 'Chardonnay puro sem madeira, com alta expressão de calcário kimmeridgiano, maçã verde, limão e ostras.', 390.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (137, 'Sancerre Blanc Pascal Jolivet (Vale do Loire)', 'Sauvignon Blanc límpido e vibrante com notas cítricas de grapefruit, pedra molhada e grama recém-cortada.', 290.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (138, 'Meursault Les Narvaux Louis Jadot', 'Chardonnay com passagem por barrica trazendo aroma sedutor de avelãs tostadas, brioche quente e manteiga fresca.', 580.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (139, 'Pinot Grigio Friuli DOC Livio Felluga', 'Branco italiano fresco com notas de pera williams, flores brancas e acidez equilibrada que limpa o paladar.', 230.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (140, 'Gavi di Gavi DOCG Villa Sparina (Piemonte)', 'Elaborado com a uva Cortese, seco, fino, com aromas de pêssego branco, amêndoa amarga e excelente persistência.', 210.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (141, 'Vinho Verde Alvarinho Soalheiro Primeiras Vinhas', 'O mais expressivo alvarinho de Monção e Melgaço, acidez cintilante, notas de maracujá doce e grande mineralidade.', 195.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (142, 'Sauvignon Blanc Cloudy Bay (Marlborough)', 'Ícone mundial neozelandês com aromas exuberantes de maracujá, folha de tomate, lima e final fresco cristalino.', 330.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (143, 'Chardonnay Catena Alta White Stones (Gualtallary)', 'Chardonnay de solo aluvial e calcário, notas salinas, maçã madura e acidez vibrante de vinhedo extremo.', 490.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1584916201218-f4242ceb4809?auto=format&fit=crop&w=800&q=80'),
    (144, "Rosé de Provence Whispering Angel Château d'Esclans", 'O rosé mais famoso do mundo, cor casca de cebola pálida, notas de pêssego, melão maduro e toque mineral fino.', 260.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1558001373-4b934520921c?auto=format&fit=crop&w=800&q=80'),
    (145, 'Champagne Dom Pérignon Brut Vintage', 'O ápice do prestígio em Champagne, bolhas microscópicas, brioche, frutas secas, mineralidade profunda e elegância.', 1850.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'),
    (146, 'Champagne Veuve Clicquot Ponsardin Brut', 'Famoso rótulo amarelo com predominância de Pinot Noir trazendo força aromática, frescor cítrico e cremosidade.', 460.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'),
    (147, "Espumante Franciacorta Ca' del Bosco Cuvée Prestige", 'O método tradicional italiano da Lombardia, envelhecido por 25 meses sobre as borras com cremosidade sem igual.', 380.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'),
    (148, 'Prosecco di Valdobbiadene Superiore DOCG Santa Margherita', 'Espumante italiano aromático, perlage fino e persistente com notas florais de acácia e maçã golden.', 175.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'),
    (149, 'Espumante Brasileiro Casa Valduga 130 Brut (Vale dos Vinhedos)', 'Elaborado pelo método tradicional com 36 meses de autólise, aromas de amêndoas tostadas e acidez viva.', 180.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1569919659476-f0852f6834b7?auto=format&fit=crop&w=800&q=80'),
    (150, "Vinho do Porto Graham's Tawny 20 Anos 750ml", 'Vinho licoroso fortificado envelhecido em cascos de carvalho, notas ricas de nozes, casca de laranja e figos secos.', 460.0, 'CARTA DE VINHOS', 'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80'),
]


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db() -> None:
    """Cria as tabelas (se nao existirem) e popula os produtos uma unica vez."""
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco NUMERIC NOT NULL CHECK (preco >= 0),
            categoria TEXT NOT NULL,
            imagem TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            cliente TEXT NOT NULL,
            mesa TEXT NOT NULL,
            pagamento TEXT NOT NULL,
            observacoes TEXT,
            subtotal NUMERIC NOT NULL,
            taxa_servico NUMERIC NOT NULL DEFAULT 0,
            total NUMERIC NOT NULL,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            nome TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            total NUMERIC NOT NULL
        );
        """
    )
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO produtos (id, nome, descricao, preco, categoria, imagem) VALUES (?, ?, ?, ?, ?, ?)",
            PRODUTOS_SEED,
        )
    db.commit()
    db.close()


def produto_json(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": float(row["preco"]),
        "categoria": row["categoria"],
        "imagem": row["imagem"],
    }


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/products")
def listar_produtos():
    db = get_db()
    rows = db.execute("SELECT * FROM produtos ORDER BY id").fetchall()
    db.close()
    return jsonify({"products": [produto_json(r) for r in rows]})


@app.post("/api/orders")
def criar_pedido():
    payload = request.get_json(silent=True) or {}
    cliente = str(payload.get("cliente", "")).strip()
    mesa = str(payload.get("mesa", "")).strip()
    pagamento = str(payload.get("pagamento", "")).strip()
    observacoes = str(payload.get("observacoes", "")).strip()
    com_taxa_servico = bool(payload.get("taxa_servico", True))
    itens_recebidos = payload.get("itens") or []

    if not cliente or not mesa or not pagamento or not itens_recebidos:
        return jsonify({"error": "Informe cliente, mesa, pagamento e pelo menos um item."}), 400

    quantidades: dict[int, int] = {}
    for item in itens_recebidos:
        try:
            produto_id = int(item["produto_id"])
            quantidade = int(item["quantidade"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Item de pedido invalido."}), 400
        if not 1 <= quantidade <= 99:
            return jsonify({"error": "A quantidade de cada item deve estar entre 1 e 99."}), 400
        quantidades[produto_id] = quantidades.get(produto_id, 0) + quantidade

    db = get_db()
    try:
        placeholders = ",".join("?" for _ in quantidades)
        rows = db.execute(
            f"SELECT * FROM produtos WHERE id IN ({placeholders})", tuple(quantidades)
        ).fetchall()
        if len(rows) != len(quantidades):
            return jsonify({"error": "Um ou mais produtos nao foram encontrados."}), 400

        itens = []
        subtotal = 0.0
        for row in rows:
            quantidade = quantidades[row["id"]]
            total_item = round(float(row["preco"]) * quantidade, 2)
            subtotal += total_item
            itens.append({
                "produto_id": row["id"],
                "nome": row["nome"],
                "preco": float(row["preco"]),
                "quantidade": quantidade,
                "total": total_item,
            })
        subtotal = round(subtotal, 2)
        taxa_servico = round(subtotal * 0.10, 2) if com_taxa_servico else 0.0
        total = round(subtotal + taxa_servico, 2)
        numero = f"CO-{uuid4().hex[:8].upper()}"

        cursor = db.execute(
            "INSERT INTO pedidos (numero, cliente, mesa, pagamento, observacoes, subtotal, taxa_servico, total) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (numero, cliente, mesa, pagamento, observacoes, subtotal, taxa_servico, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, nome, preco, quantidade, total) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["nome"], item["preco"], item["quantidade"], item["total"]),
            )
        db.commit()

        pedido = {
            "numero": numero, "cliente": cliente, "mesa": mesa, "pagamento": pagamento,
            "observacoes": observacoes, "subtotal": subtotal, "taxa_servico": taxa_servico,
            "total": total, "itens": itens,
        }
        return jsonify({"order": pedido}), 201
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
