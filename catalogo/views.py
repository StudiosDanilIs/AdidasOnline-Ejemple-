from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy, reverse
from functools import wraps
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
import re
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors

from .models import Producto, Carrito, Compra, DetalleCompra, Usuario
from .forms import ProductoForm, RegistroForm, LoginForm, RecuperarCuentaForm
import secrets

# ========================= VISTAS GENERALES =========================
def home(request):
    productos = Producto.objects.all()
    return render(request, "catalogo/index.html", {"productos": productos})


def categorias(request):
    productos = Producto.objects.all()
    return render(request, "catalogo/categorias.html", {"productos": productos})


def politica(request):
    return render(request, "catalogo/politica.html")


def patrocicado(request):
    equipos = [
        {
            "nombre": "FC Bayern Munich",
            "liga": "Bundesliga",
            "descripcion": "32 títulos de Bundesliga y 6 Champions League con equipación Adidas",
            "imagen": "https://nbcsports.brightspotcdn.com/dims4/default/3399ccd/2147483647/strip/true/crop/4911x2762+0+0/resize/1440x810!/format/webp/quality/90/?url=https%3A%2F%2Fnbc-sports-production-nbc-sports.s3.us-east-1.amazonaws.com%2Fbrightspot%2F4b%2F65%2F6b9602447c168415539ac71d05fd%2Fgettyimages-1268078305-e1598217140643.jpg",
            "imagenes": [
                "https://media.gettyimages.com/id/1692597354/es/foto/munich-germany-players-of-bayern-munich-line-up-for-a-team-photo-prior-to-the-uefa-champions.jpg?s=1024x1024&w=gi&k=20&c=IDrqgdz1-oGAw5mMc0CGCFS1pwMf02s7S28FJ2sNm08=",
                "https://media.gettyimages.com/id/1493867181/es/foto/cologne-germany-manuel-neuer-of-fc-bayern-munich-lifts-the-bundesliga-meisterschale-trophy.jpg?s=1024x1024&w=gi&k=20&c=kZMJYbe1grZBPtHlx7XMfEgXWBXbhbD9oY21NGUy8Y4=",
            ],
            "info_adicional": "El FC Bayern Munich es uno de los clubes más exitosos de Alemania y Europa. Con más de 30 títulos de Bundesliga y 6 Champions League, el Bayern es conocido por su estilo de juego ofensivo y su cantera de talentos. Fundado en 1900, el club ha dominado el fútbol alemán y ha sido un contendiente constante en competiciones europeas. Adidas, fundada en Baviera, ha sido su proveedor de kits desde 1974, creando diseños innovadores como los que incluyen tecnología climacool y primegreen.",
        },
        {
            "nombre": "Real Madrid CF",
            "liga": "LaLiga",
            "descripcion": "14 Champions League y 35 Ligas con Adidas",
            "imagen": "https://i0.wp.com/realsoccerclub.org/wp-content/uploads/2022/05/avc8199_thumb-real-madrid-campeones-de-europa-14-veces-levantan-el-trofeo.jpg?ssl=1",
            "imagenes": [
                "https://media.gettyimages.com/id/1933188848/es/foto/riyadh-saudi-arabia-nacho-fernandez-of-real-madrid-lifts-the-super-copa-de-espa%C3%B1a-trophy-after.jpg?s=1024x1024&w=gi&k=20&c=kNUCnNslffTEa5tin072PY-A_wJgZgDFwFSrnF-VrWU=",
                "https://media.gettyimages.com/id/1922846246/es/foto/riyadh-saudi-arabia-antonio-ruediger-and-nacho-fernandez-of-real-madrid-celebrate-after.jpg?s=1024x1024&w=gi&k=20&c=lYjQKlISTP7eEx3YsHCiIRI1H6Fexh7BZnH_eTJn7iE=",
            ],
            "info_adicional": "El Real Madrid es el club más exitoso en la historia de la Champions League, con 14 títulos. También ha ganado 35 Ligas españolas y es conocido por su política de fichar a las mayores estrellas del fútbol. Fundado en 1902, el Real Madrid es un símbolo de excelencia y tradición en el fútbol mundial. Adidas fue su proveedor de kits entre 1998 y 2020, período en el que el club ganó 5 Champions League, incluyendo el tricampeonato entre 2016 y 2018.",
        },
        {
            "nombre": "Manchester United",
            "liga": "Premier League",
            "descripcion": "20 títulos de Premier League y 3 Champions League",
            "imagen": "https://media.gettyimages.com/id/2155249794/es/foto/london-england-bruno-fernandes-of-manchester-united-holds-aloft-the-emirates-fa-cup-trophy-in.jpg?s=1024x1024&w=gi&k=20&c=cbOBoO0HErfblxoPR1j_aPkBokDrgeFQ9XfnWE8tZ7U=",
            "imagenes": [
                "https://media.gettyimages.com/id/2154620677/es/foto/london-england-alejandro-garnacho-of-manchester-united-celebrates-with-his-winners-medal-after.jpg?s=1024x1024&w=gi&k=20&c=iCRSQeHP1KhHk7ZK2TpaXpPlMV9aUZHSwJ1yvcN1GMM=",
                "https://media.gettyimages.com/id/1722639535/es/foto/manchester-england-scott-mctominay-of-manchester-united-celebrates-scoring-the-winning-goal.jpg?s=1024x1024&w=gi&k=20&c=hZ6dMBEViEasdPnOxvQ_J1JMh5GOstw_-cxkaEWztxs=",
            ],
            "info_adicional": "El Manchester United es uno de los clubes más populares del mundo. Con una rica historia y una gran cantidad de títulos, el United es conocido por su estilo de juego atractivo y su cantera de jóvenes talentos. Fundado en 1878, el club ha sido un referente en el fútbol inglés y europeo. Adidas fue su proveedor de kits entre 2015 y 2021, período en el que el club ganó la Europa League 2017 y la Copa de la Liga 2017.",
        },
        {
            "nombre": "Boca Juniors",
            "liga": "Primera División de Argentina",
            "descripcion": "34 títulos de Primera División y 6 Copas Libertadores",
            "imagen": "https://media.gettyimages.com/id/1296955039/es/foto/san-juan-argentina-carlos-t%C3%A9vez-of-boca-juniors-lifts-the-trophy-to-celebrate-with-teammates.jpg?s=1024x1024&w=gi&k=20&c=EutAod6HObNol-HzFdOrQ7ptGspQGooXU6OwUzVKWVg=",
            "imagenes": [
                "https://media.gettyimages.com/id/2187280028/es/foto/buenos-aires-argentina-milton-gimenez-of-boca-juniors-celebrates-after-scoring-the-first-goal.jpg?s=1024x1024&w=gi&k=20&c=HodkBeQuvlVeG02ASGIDwyK3bHH1piaPhD84nvDd7GI=",
                "https://media.gettyimages.com/id/1357982546/es/foto/santiago-del-estero-argentina-carlos-izquierdoz-of-boca-juniors-and-teammates-celebrate-with.jpg?s=1024x1024&w=gi&k=20&c=ua7xczFNqFv5a6b3fQQ5u2tlSjmZ-FMcfqv57AsaozM=",
            ],
            "info_adicional": "Boca Juniors es uno de los clubes más exitosos de Argentina y Sudamérica. Con una gran cantidad de títulos nacionales e internacionales, Boca es conocido por su pasión y su hinchada. Fundado en 1905, el club es un ícono del fútbol sudamericano. Adidas ha sido su proveedor de kits desde 2019, creando diseños que combinan las rayas azules y amarillas con detalles modernos inspirados en La Bombonera.",
        },
        {
            "nombre": "Ajax",
            "liga": "Eredivisie",
            "descripcion": "36 títulos de Eredivisie y 4 Champions League",
            "imagen": "https://phantom-marca-us.unidadeditorial.es/7b81da8a534e17c87abeaf696a9e8e37/resize/828/f/webp/assets/multimedia/imagenes/2022/05/11/16523023050945.jpg",
            "imagenes": [
                "https://es.coachesvoice.com/wp-content/uploads/2019/04/featured-13.jpg",
                "https://media.gettyimages.com/id/1242499619/es/foto/amsterdam-netherlands-antony-of-ajax-celebrates-his-2-1-during-the-dutch-eredivisie-match.jpg?s=1024x1024&w=gi&k=20&c=gxn2Jnd6xfDN5u_Qpclk94zmtAUNaYB43ZIU2NjPB3k=",
            ],
            "info_adicional": "El Ajax es conocido por su filosofía de juego ofensivo y su cantera de jóvenes talentos. Ha ganado múltiples títulos en Holanda y Europa. Fundado en 1900, el club es famoso por su estilo de juego 'fútbol total' y por haber formado a grandes estrellas como Johan Cruyff. Adidas ha sido su proveedor de kits en varias etapas, incluyendo la actual, donde ha respetado el diseño clásico de rayas rojas y blancas mientras introduce toques modernos.",
        },
    ]

    selecciones = [
        {
            "nombre": "Venezuela",
            "confederacion": "CONMEBOL",
            "descripcion": "Selección nacional de fútbol de Venezuela",
            "imagen": "https://cdn.conmebol.com/wp-content/uploads/2017/06/pena_vene.1.jpg",
            "imagenes": [
                "https://media.gettyimages.com/id/1892666/es/foto/seattle-the-venezuela-national-team-poses-for-a-team-photo-prior-to-a-friendly-soccer-match.jpg?s=1024x1024&w=gi&k=20&c=Apb2pVTKgQah9hxOADQaQzqm-xuXvLC1s_nI41yE_RI=",
                "https://media.gettyimages.com/id/2159449466/es/foto/inglewood-california-players-of-venezuela-celebrate-during-the-conmebol-copa-america-2024.jpg?s=1024x1024&w=gi&k=20&c=l444iBB0dHY0Ur2Y0DKSC5_iDl2QOvK7Bu-GIMc1Eqg=",
            ],
            "info_adicional": "La selección de Venezuela es conocida por su crecimiento en los últimos años y su participación en torneos internacionales. Aunque no ha ganado títulos importantes, ha mostrado un progreso significativo en competiciones como la Copa América. Adidas ha sido su proveedor de kits desde 2017, ayudando a consolidar su identidad visual.",
        },
        {
            "nombre": "Argentina",
            "confederacion": "CONMEBOL",
            "descripcion": "Campeona del Mundo en 2022",
            "imagen": "https://media.gettyimages.com/id/2162062794/es/foto/miami-gardens-florida-lionel-messi-of-argentina-celebrates-with-the-trophy-after-the-teams.jpg?s=1024x1024&w=gi&k=20&c=gUSbRuoCV3S89G6G1zNCl8FsaI8khIjM2FW8V05Ol4I=",
            "imagenes": [
                "https://media.gettyimages.com/id/1451363359/es/foto/lusail-city-qatar-lionel-messi-of-argentina-lifts-the-fifa-world-cup-qatar-2022-winners-trophy.jpg?s=1024x1024&w=gi&k=20&c=Y1_Vfsk4QiYV2FDIIdZotGjsWG0ehUNGnTtkZf3-Wfw=",
                "https://media.gettyimages.com/id/1676842455/es/foto/la-paz-bolivia-lionel-messi-of-argentina-talks-with-leandro-paredes-of-argentina-in-the-bench.jpg?s=1024x1024&w=gi&k=20&c=rcYmE7oCJw54qGhHOXQ7CbqGO_8LymTzwoe5VtEEiH8=",
                "https://media.gettyimages.com/id/2161509701/es/foto/topshot-argentinas-forward-lionel-messi-lifts-up-the-trophy-as-he-celebrates-winning-the.jpg?s=1024x1024&w=gi&k=20&c=4BS-24bh9rZLVl1CZxzjNgTHWSqwKMFtvvHcC24QfRY=",
            ],
            "info_adicional": "La selección argentina es una de las más exitosas del mundo, con múltiples Copas América y un reciente título mundial en 2022. Conocida como 'La Albiceleste', Argentina ha sido hogar de grandes leyendas como Diego Maradona y Lionel Messi. Adidas ha sido su proveedor de kits desde 1974, creando diseños icónicos como el de la Copa del Mundo 2022, que combinaba las rayas celestes y blancas con tecnología HEAT.RDY.",
        },
        {
            "nombre": "Colombia",
            "confederacion": "CONMEBOL",
            "descripcion": "Selección nacional de fútbol de Colombia",
            "imagen": "https://media.gettyimages.com/id/2107851912/es/foto/colombias-players-pose-prior-to-the-international-friendly-football-match-between-romania-and.jpg?s=1024x1024&w=gi&k=20&c=Ixm9ANUfmXZVyZNMECBFUYnl-_uyOnSknlnfgfOSu_U=",
            "imagenes": [
                "https://media.gettyimages.com/id/2178606206/es/foto/barranquilla-colombia-luis-diaz-of-colombia-celebrates-with-teammates-james-rodriguez-and.jpg?s=1024x1024&w=gi&k=20&c=esP8f-w7QjtbuK6p35TRnWXQJc95GA1u8f_-YVeO8AQ=",
                "https://media.gettyimages.com/id/2107852033/es/foto/colombias-forward-jhon-cordoba-celebrates-with-colombias-midfielder-james-rodriguez-scoring.jpg?s=1024x1024&w=gi&k=20&c=0VQJJ6o4qksDzu7ed2fC8OaYxOh4tBCwdNyH5MArH_c=",
            ],
            "info_adicional": "La selección de Colombia es conocida por su talento y su participación en torneos internacionales. Aunque no ha ganado un Mundial, ha tenido grandes actuaciones en Copas América y Mundiales, destacando jugadores como Carlos Valderrama y James Rodríguez. Adidas ha sido su proveedor de kits desde 2011, creando diseños que reflejan la vibrante cultura colombiana.",
        },
        {
            "nombre": "Japón",
            "confederacion": "AFC",
            "descripcion": "Selección nacional de fútbol de Japón",
            "imagen": "https://e00-marca.uecdn.es/assets/multimedia/imagenes/2019/01/31/15489554727875.jpg",
            "imagenes": [
                "https://media.gettyimages.com/id/1671383016/es/foto/wolfsburg-germany-the-players-of-japan-line-up-during-the-international-friendly-match-between.jpg?s=1024x1024&w=gi&k=20&c=E-D5byl7cIC0f1TNQx0EckWSebxcjqybyZG3HVTCxBs=",
                "https://media.gettyimages.com/id/1670412922/es/foto/wolfsburg-germany-ao-tanaka-of-japan-celebrates-with-teammate-takefusa-kubo-after-scoring-the.jpg?s=1024x1024&w=gi&k=20&c=xdxHqoE6NR-i_KEIDKVpxQmYZVIFFFiDjtqkTwttIjU=",
            ],
            "info_adicional": "Japón es una de las selecciones más fuertes de Asia, con múltiples participaciones en Copas del Mundo. Conocida como 'Los Samuráis Azules', Japón ha mostrado un fútbol disciplinado y técnico en competiciones internacionales. Adidas ha sido su proveedor de kits desde 1999, creando diseños que combinan tradición y modernidad.",
        },
        {
            "nombre": "España",
            "confederacion": "UEFA",
            "descripcion": "Campeona del Mundo en 2010",
            "imagen": "https://media.gettyimages.com/id/525842364/es/foto/sergio-ramos-of-spain-lifts-the-fifa-world-cup-trophy-after-defeating-the-netherlands-0-1.jpg?s=1024x1024&w=gi&k=20&c=4FD1rY_wi5kkqw8l6Nbe5TtPoNTJLI97fNF8GjQrq90=",
            "imagenes": [
                "https://media.gettyimages.com/id/1258800280/es/foto/rotterdam-netherlands-unai-simon-of-spain-jordi-alba-of-spain-aymeric-laporte-of-spain-robin.jpg?s=1024x1024&w=gi&k=20&c=IukD95iwXxxBhoBxCsLtYc2k7Rvm9nG1weqKfrkL7N4=",
                "https://media.gettyimages.com/id/1660626003/es/foto/16-spains-midfielder-mikel-merino-spains-defender-aymeric-laporte-spains-defender-robin-le.jpg?s=1024x1024&w=gi&k=20&c=lX3zqLens7TN1Pb-4HtqY_qw8bPoyiJReBFZm5sk9sg=",
            ],
            "info_adicional": "España es conocida por su estilo de juego de posesión y su victoria en la Copa del Mundo 2010. Conocida como 'La Roja', España dominó el fútbol mundial entre 2008 y 2012, ganando dos Eurocopas y un Mundial con un estilo de juego basado en el control del balón. Adidas ha sido su proveedor de kits desde 1991, creando diseños que reflejan la identidad española.",
        },
    ]

    estrellas = [
        {
            "nombre": "Lionel Messi",
            "deporte": "Fútbol",
            "descripcion": "8 Balones de Oro y embajador global desde 2006",
            "imagen": "https://phantom-marca-us.unidadeditorial.es/682a503fbe81c445114a135797f8187f/resize/828/f/webp/assets/multimedia/imagenes/2024/11/01/17304359963617.jpg",
            "imagenes": [
                "https://media.gettyimages.com/id/1191655197/es/foto/paris-france-lionel-messi-poses-onstage-after-winning-his-sixth-ballon-dor-award-during-the.jpg?s=1024x1024&w=gi&k=20&c=1VZthjIDMkIfvBJWfgD-YJ_RoUMJ-dz2xKprnwv9JLQ=",
                "https://www.modernnotoriety.com/wp-content/uploads/2024/08/messi-adidas-gazelle-IH81560-triunfo-dorado-release-date-1024x536.jpg",
                "https://media.gettyimages.com/id/1626495282/es/foto/nashville-tennessee-lionel-messi-of-inter-miami-poses-with-his-best-player-award-and-top.jpg?s=1024x1024&w=gi&k=20&c=EpwAlZ7jTIm8UBd2HQYgV3ogc4V5HZTe_BeoWaibeL8=",
            ],
            "info_adicional": "Lionel Messi es considerado uno de los mejores futbolistas de todos los tiempos. Ha ganado múltiples títulos con el FC Barcelona y la selección argentina, incluyendo la Copa del Mundo 2022. Messi es conocido por su habilidad, visión de juego y capacidad goleadora. Adidas ha sido su patrocinador desde 2006, creando botas personalizadas como las Predator y X, que han sido parte de sus mayores logros.",
        },
        {
            "nombre": "Toni Kroos",
            "deporte": "Fútbol",
            "descripcion": "Mediocampista del Real Madrid y la selección alemana",
            "imagen": "https://media.gettyimages.com/id/2157109962/es/foto/herzogenaurach-germany-toni-kroos-of-germany-talks-to-the-media-during-a-press-conference-at.jpg?s=1024x1024&w=gi&k=20&c=iHqjGWktYTwgs6BeZB92I49GgGfg5pTBLFcdQg3BwCU=",
            "imagenes": [
                "https://pxcdn.meridiano.net/052024/1716306644879.webp?cw=1155&ch=650&extw=jpg",
                "https://www.marketingregistrado.com/img/noticias/big/botines-que-lanzo-adidas-honor-toni-kroos_(2).webp",
            ],
            "info_adicional": "Toni Kroos es conocido por su precisión en el pase y su visión de juego. Ha ganado múltiples Champions League con el Real Madrid y fue una pieza clave en la selección alemana que ganó el Mundial en 2014. Kroos es admirado por su elegancia y control en el mediocampo. Adidas ha sido su patrocinador durante años, creando botas que reflejan su estilo de juego.",
        },
        {
            "nombre": "Mohamed Salah",
            "deporte": "Fútbol",
            "descripcion": "Delantero del Liverpool y la selección egipcia",
            "imagen": "https://i.dailymail.co.uk/1s/2018/10/12/22/5007404-0-image-a-69_1539379924332.jpg",
            "imagenes": [
                "https://runfun.net/wp-content/uploads/2023/03/Mo-Salah-Adidas-2.png",
                "https://media.gettyimages.com/id/1642474564/es/foto/newcastle-upon-tyne-england-mohamed-salah-of-liverpool-looks-on-prior-to-the-premier-league.jpg?s=1024x1024&w=gi&k=20&c=qQmu10B7J1-5Q84QI9G8SuSdCsiJCHdn-F9mbhnYFE0=",
            ],
            "info_adicional": "Mohamed Salah es uno de los mejores delanteros del mundo, conocido por su velocidad y su habilidad goleadora. Con el Liverpool, ha ganado la Premier League y la Champions League. Salah es un ícono en Egipto y un referente en el fútbol africano. Adidas ha sido su patrocinador, creando botas personalizadas que reflejan su estilo de juego explosivo.",
        },
        {
            "nombre": "Alexander Zverev",
            "deporte": "Tenis",
            "descripcion": "Tenista alemán, campeón de Grand Slam",
            "imagen": "https://www.lanacion.com.ar/resizer/v2/alexander-zverev-ganador-en-cincinnati-el-aleman-QUTTWFZEOZHHZKG2ENLJEH7CQM.JPG?auth=bd4d7cd7bf4a580d0c071ddd009e6e5016f51eebdee014507f9aabe750bdf4fa&width=880&height=586&quality=70&smart=true",
            "imagenes": [
                "https://media.gettyimages.com/id/1331758023/es/foto/tokyo-japan-gold-medalist-alexander-zverev-of-team-germany-poses-on-the-podium-during-the.jpg?s=1024x1024&w=gi&k=20&c=FWEOkJ_8XQM47EWfu143gYigiG3v-D_5YaDaVQgkwTQ=",
                "https://media.gettyimages.com/id/1331428487/es/foto/tokyo-japan-alexander-zverev-of-team-germany-plays-a-backhand-during-his-mens-singles.jpg?s=1024x1024&w=gi&k=20&c=8bQNcV297pqKWQ-uJUG3roP4EEgMclRaS4JYQCWXBQo=",
                "https://media.gettyimages.com/id/1331758053/es/foto/tokyo-japan-alexander-zverev-of-team-germany-celebrates-victory-after-his-mens-singles-gold.jpg?s=1024x1024&w=gi&k=20&c=BRhQqGyF0L7m4xpUN8_ndms97_v8QUbcPaaqqRrWPY4=",
            ],
            "info_adicional": "Alexander Zverev es uno de los mejores tenistas del mundo, con múltiples títulos de Grand Slam. Ganó la medalla de oro en los Juegos Olímpicos de Tokio 2020 y ha sido una figura destacada en el circuito ATP. Zverev es conocido por su potente saque y su juego desde el fondo de la pista. Adidas ha sido su patrocinador, proporcionándole ropa y calzado que combinan rendimiento y estilo.",
        },
        {
            "nombre": "Lamine Yamal",
            "deporte": "Fútbol",
            "descripcion": "Joven promesa del FC Barcelona",
            "imagen": "https://media.gettyimages.com/id/2190111008/es/foto/barcelona-spain-lamine-yamal-of-fc-barcelona-is-presented-with-the-golden-boy-2024-award-prior.jpg?s=1024x1024&w=gi&k=20&c=QM41aZ7mNdZbByGCS-4FaOEpJSnubOHC56WePHN2IC4=",
            "imagenes": [
                "https://preview.thenewsmarket.com/Previews/ADID/StillAssets/960x540/685133.jpg",
                "https://media.gettyimages.com/id/2161387390/es/foto/munich-germany-lamine-yamal-of-spain-poses-for-a-photo-with-the-vivo-player-of-the-match-award.jpg?s=1024x1024&w=gi&k=20&c=643U7dxGmnQEymoqS4ItGWQbcOm0vfyc-Td8C8xDNTc=",
                "https://media.gettyimages.com/id/2180922599/es/foto/barcelonas-spanish-forward-lamine-yamal-receives-the-kopa-trophy-for-best-under-21-player.jpg?s=1024x1024&w=gi&k=20&c=IwjQj4_NIBblWRIZKm1zyJj75PMiEZa3kKa3o3tl35s=",
            ],
            "info_adicional": "Lamine Yamal es una de las jóvenes promesas del FC Barcelona, conocido por su velocidad y habilidad. Con solo 16 años, ya ha debutado en el primer equipo y ha mostrado un potencial enorme. Yamal es considerado uno de los futuros grandes del fútbol mundial. Adidas ha sido su patrocinador desde el inicio de su carrera, apoyando su desarrollo con equipamiento de alta calidad.",
        },
        {
            "nombre": "Ada Hegerberg",
            "deporte": "Fútbol",
            "descripcion": "Delantera del Olympique Lyonnais y la selección noruega",
            "imagen": "https://www.ellas.pa/resizer/v2/72YV6W6FBZGVRJMXELHWFO7OGA.jpg?auth=71a7e6da7e8f64e00a3365b4c84a88f65fe140540d3a8c6265bb9a1196376344&width=1200",
            "imagenes": [
                "https://media.gettyimages.com/id/1398556997/es/foto/turin-italy-ada-hegerberg-of-olympique-lyonnais-poses-with-the-uefa-womens-champions-league.jpg?s=1024x1024&w=gi&k=20&c=RH7Eg_5BJ02nlmaT4bNDPp7vqXkOphfUZ475aBW_ZUA=",
                "https://media.gettyimages.com/id/2174738894/es/foto/lyon-france-ada-hegerberg-of-olympique-lyonnais-poses-for-a-portrait-during-the-olympique.jpg?s=1024x1024&w=gi&k=20&c=3vlHMSW6623lks7x9VXgTGS5PHDD42rJXjvWGu9APIo=",
            ],
            "info_adicional": "Ada Hegerberg es una de las mejores futbolistas del mundo, conocida por su habilidad goleadora. Ha ganado múltiples Champions League con el Olympique Lyonnais y fue la primera ganadora del Balón de Oro Femenino en 2018. Hegerberg es un ícono del fútbol femenino y una inspiración para muchas jóvenes jugadoras. Adidas ha sido su patrocinador, apoyando su carrera y promoviendo el crecimiento del fútbol femenino.",
        },
    ]

    return render(
        request,
        "catalogo/patrocicado.html",
        {
            "equipos": equipos,
            "selecciones": selecciones,
            "estrellas": estrellas,
        },
    )


# ========================= VISTAS DEL CARRITO =========================
@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == "POST":
        producto = get_object_or_404(Producto, id=producto_id)
        talla = request.POST.get("talla")
        cantidad = int(request.POST.get("cantidad", 1))

        carrito_item, created = Carrito.objects.get_or_create(
            usuario=request.user,  # Cambiado de cliente a usuario
            producto=producto,
            talla=talla,
            defaults={"cantidad": cantidad},
        )

        if not created:
            carrito_item.cantidad += cantidad
            carrito_item.save()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@login_required
def ver_carrito(request):
    carrito_items = Carrito.objects.filter(usuario=request.user)
    total = sum(item.subtotal() for item in carrito_items)
    return render(
        request,
        "catalogo/carrito.html",
        {"carrito_items": carrito_items, "total": total},
    )


@login_required
def eliminar_del_carrito(request, item_id):
    if request.method == "POST":
        carrito_item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
        carrito_item.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@login_required
def actualizar_cantidad(request, item_id):
    if request.method == "POST":
        carrito_item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
        cantidad = int(request.POST.get("cantidad"))
        carrito_item.cantidad = cantidad
        carrito_item.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


# ========================= VISTAS DE COMPRAS =========================
@login_required
def completar_compra(request):
    carrito_items = Carrito.objects.filter(usuario=request.user)

    if not carrito_items:
        messages.warning(request, "Tu carrito está vacío")
        return redirect("home")

    total = sum(item.subtotal() for item in carrito_items)

    if request.method == "POST":
        try:
            metodo_pago = request.POST.get("metodo_pago")
            direccion = request.POST.get("direccion", "").strip()

            if not direccion:
                raise ValueError("La dirección de entrega es requerida")

            # Validación de método de pago
            if metodo_pago not in dict(Compra.METODO_PAGO_OPCIONES):
                raise ValueError("Método de pago inválido")

            compra = Compra.objects.create(
                usuario=request.user,  # Cambiado de cliente a usuario
                total=total,
                direccion_entrega=direccion,
                metodo_pago=metodo_pago,
                transaccion_id=f"{metodo_pago}-{uuid.uuid4().hex[:8]}",
            )

            for item in carrito_items:
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_actual,
                    subtotal=item.subtotal(),
                )

            carrito_items.delete()
            request.session["ultima_compra_id"] = compra.id
            return redirect("compra_exitosa")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("completar_compra")

    return render(
        request,
        "catalogo/procesar_pago.html",
        {"total": total, "carrito_items": carrito_items},
    )


@login_required
def compra_exitosa(request):
    if "ultima_compra_id" not in request.session:
        return redirect("home")
    return render(request, "catalogo/compra_exitosa.html")


@login_required
def descargar_comprobante(request):
    compra_id = request.session.get("ultima_compra_id")
    if not compra_id:
        return redirect("home")

    try:
        compra = Compra.objects.get(id=compra_id, usuario=request.user)
    except Compra.DoesNotExist:
        return redirect("home")

    # Crear respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="comprobante_{compra.transaccion_id}.pdf"'
    )

    # Configurar PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Comprobante de Compra")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, f"Transacción ID: {compra.transaccion_id}")

    # Información del cliente
    y_position = height - 120
    info_cliente = [
        f"Cliente: {request.user.nombre}",
        f"Fecha: {compra.fecha.strftime('%d/%m/%Y %H:%M')}",
        f"Método de pago: {compra.metodo_pago}",
        f"Dirección de entrega: {compra.direccion_entrega}",
    ]

    for linea in info_cliente:
        p.drawString(50, y_position, linea)
        y_position -= 20

    # Tabla de productos
    detalles = DetalleCompra.objects.filter(compra=compra)
    datos_tabla = [["Producto", "Cantidad", "P. Unitario", "Subtotal"]]
    for detalle in detalles:
        datos_tabla.append(
            [
                detalle.producto.nombre,
                str(detalle.cantidad),
                f"${detalle.precio_unitario:.2f}",
                f"${detalle.subtotal:.2f}",
            ]
        )

    tabla = Table(datos_tabla, colWidths=[250, 70, 90, 90])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3f87a6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    tabla.wrapOn(p, width - 100, height)
    tabla.drawOn(p, 50, y_position - 150)

    # Total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(400, y_position - 180, f"TOTAL: ${compra.total:.2f}")

    # Pie de página
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(
        50,
        40,
        "Gracias por su compra - Este documento es válido como factura electrónica",
    )

    p.showPage()
    p.save()

    # Limpiar sesión después de descargar
    if "ultima_compra_id" in request.session:
        del request.session["ultima_compra_id"]

    return response


# ========================= VISTAS DE USUARIOS =========================
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.nombre = form.cleaned_data["nombre"]  # Agregar nombre
            user.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso!")
            return redirect("home")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username").lower()  # Asegurar minúsculas
            password = form.cleaned_data.get("password")
            
            # Depuración: Verificar datos recibidos
            print(f"Intento de login con email: {email}")
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido {user.nombre}!")
                return redirect("home")
            else:
                # Depuración: Verificar por qué falla la autenticación
                print("Fallo en autenticación")
                try:
                    user = Usuario.objects.get(email=email)
                    print(f"Usuario existe pero falló autenticación. Contraseña correcta?: {user.check_password(password)}")
                except Usuario.DoesNotExist:
                    print("Usuario no existe en la base de datos")
                
                messages.error(request, "Email o contraseña incorrectos")
        else:
            messages.error(request, "Por favor corrige los errores en el formulario")
    else:
        form = LoginForm()
    
    return render(request, "usuarios/login.html", {"form": form})


def logout_view(request):
    Carrito.objects.filter(usuario=request.user).delete()
    logout(request)
    messages.success(request, "Sesión cerrada correctamente")
    return redirect("home")


def recuperar_cuenta(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()

        try:
            usuario = Usuario.objects.get(email=email)

            # Generar contraseña temporal
            temp_password = secrets.token_urlsafe(8)
            usuario.set_password(temp_password)
            usuario.save()

            # Enviar email con la contraseña temporal
            send_mail(
                "Tu contraseña temporal",
                f"""Hola {usuario.nombre},
                
Tu contraseña temporal es: {temp_password}

Por favor inicia sesión con esta contraseña y cámbiala inmediatamente.

Equipo de Soporte""",
                settings.EMAIL_HOST_USER,
                [usuario.email],
                fail_silently=False,
            )

            messages.success(
                request, "Se ha enviado una contraseña temporal a tu correo."
            )
            return redirect("login")

        except Usuario.DoesNotExist:
            messages.error(request, "No existe una cuenta con ese email.")

    return render(request, "usuarios/recuperar_cuenta.html")


# View para restablecer contraseña
def restablecer_contraseña(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "¡Contraseña actualizada! Ahora puedes iniciar sesión."
                )
                return redirect("login")
        else:
            form = SetPasswordForm(user)

        return render(request, "usuarios/restablecer_contraseña.html", {"form": form})
    else:
        messages.error(request, "Enlace inválido o expirado.")
        return redirect("recuperar_cuenta")


@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente')
            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'form': form
    })