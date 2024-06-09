import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Diccionario de hoteles
hoteles = {
    "Nombre": [],
    "Estrellas": [],
    "Ciudad": [],
    "Calificacion": [],
    "Numero de reseñas": [],
    "Precio por noche": [],
    "Direccion": [],
    "Servicios": []
}


def configurar_navegador():
    # Configuración del WebDriver
    s = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--window-size=1020,1200")
    navegador = webdriver.Chrome(service=s, options=options)
    return navegador

def navegar_y_buscar(navegador):
    # Entrar en la pagina web de Trivago
    navegador.get("https://www.trivago.com.mx/")

    # Click en el botón "¿A dónde irás?"
    btn_lugar = navegador.find_element(By.CLASS_NAME, "SearchButton_buttonWithoutIcon__VdR_v")
    btn_lugar.click()
    time.sleep(2)

    # Escribir en el buscador "México"
    txt_lugar = navegador.find_element(By.CLASS_NAME, "AutoComplete_input__6pSoh")
    txt_lugar.send_keys("México")
    time.sleep(2)

    # Click en el botón "Fecha"
    btn_fecha = navegador.find_element(By.XPATH, '//*[@id="suggestion-list"]//li[2]//div//div')
    btn_fecha.click()
    time.sleep(2)

    # Click en la opción de "Mañana por la noche"
    btn_manana_noche = navegador.find_element(By.XPATH, "//label[@data-testid='tomorrowNight-index-label']")
    btn_manana_noche.click()
    time.sleep(2)

    # Click en el botón "Buscar"
    cmbtachita = navegador.find_element(By.XPATH, '//*[@data-testid="search-button-with-loader"]')
    cmbtachita.click()
    time.sleep(10)

    # Dar click en el filtro
    list_box_filtro = navegador.find_element(By.ID, "sorting-selector")
    list_box_filtro.click()
    time.sleep(3)

    # Seleccionar filtro "Solo precio"
    opcion = navegador.find_element(By.XPATH, '//option[@value="1" and text()="Solo precio"]')
    opcion.click()
    time.sleep(10)

def extraer_datos(navegador, num_repeticiones):
    for i in range(num_repeticiones):

        # Contador de repeticiones
        print(f"Repetición {i+1}/{num_repeticiones}")

        # HTML de la página
        soup = BeautifulSoup(navegador.page_source, "html5lib")

        # Cuadros en los que se dividen los hoteles
        hotel_elements = soup.find_all("li", {"data-testid": "accommodation-list-element"})

        # Ciclo en donde se obtienen los elementos y se agregan al diccionario
    for hotel_element in hotel_elements:
        # Nombre
        hotel_name_tag = hotel_element.find("span", {"itemprop": "name"})
        if hotel_name_tag is not None:
            hotel_name = hotel_name_tag.get("title") or hotel_name_tag.text
            hoteles["Nombre"].append(hotel_name)
            print(hotel_name)
        else:
            hoteles["Nombre"].append("Sin nombre")            # Modifica

        # Estrellas
        star_elements = hotel_element.find_all("span", {"data-testid": "star"})
        if star_elements is not None:                         # Agrega
            star_count = len(star_elements)
            estrellas = int(star_count)                       # Agrega
            hoteles["Estrellas"].append(estrellas)            # Modifica

        else:
            hoteles["Estrellas"].append(0)                    # Agrega              # Modifica

        # Ciudad
        city_tag = hotel_element.find("span", {"class": "block text-left w-11/12 text-m"})
        if city_tag is not None:
            city = city_tag.text
            hoteles["Ciudad"].append(city)
        else:
            hoteles["Ciudad"].append("Sin Ciudad")             # Modifica

        # Calificación
        rating_tag = hotel_element.find("span", {"itemprop": "ratingValue"})
        if rating_tag is not None:
            rating = rating_tag.text
            calificacion = float(rating)                       # Agrega
            hoteles["Calificacion"].append(calificacion)       # Modifica
        else:
            hoteles["Calificacion"].append(0)                  # Modifica

        # Número de reseñas
        reviews_meta = hotel_element.find("meta", {"itemprop": "ratingCount"})
        if reviews_meta is not None:
            reviews = reviews_meta["content"]
            resenas = int(reviews)                             # Agrega
            hoteles["Numero de reseñas"].append(resenas)       # Modifica
        else:
            hoteles["Numero de reseñas"].append(0)             # Modifica

        # Precio                                              # Agrega
        try:
            price_tag = hotel_element.find("span", {"data-testid": "recommended-price"})
            if price_tag is not None:
                price = price_tag.text
                price = price.lstrip("$")                     # Agrega
            else:
                price = 0                                     # Modifica
        except Exception as e:
            print(f"Error al obtener el precio: {e}")
            price = 0                                         # Modifica
        precio = int(price)                                   # Agrega
        hoteles["Precio por noche"].append(precio)            # Modifica

        # Encuentra y hace clic en todos los botones donde se despliega info
        botones_info = navegador.find_elements(By.XPATH, '//button[@data-testid="distance-label-section"]')


        for boton in botones_info:
            try:
                # Click en el boton info
                boton.click()
                time.sleep(2)

                # Click en boton servicos
                boton_servicios = navegador.find_element(By.CSS_SELECTOR, 'button.text-blue-700.text-m.text-left.py-1.outline-none.focus\\:outline-none.font-bold[data-testid="toggle-all-amenities"]')
                boton_servicios.click()
                time.sleep(2)

                # Extrae la información de contacto
                soup2 = BeautifulSoup(navegador.page_source, "html5lib")

                # Dirección
                address_element = soup2.find("address", {"data-testid": "info-slideout-map-address"})
                ul_element = address_element.find("ul", {"itemtype": "https://schema.org/PostalAddress"})
                if ul_element:
                    li_elements = ul_element.find_all("li")
                    contacto_info = " ".join([li.text for li in li_elements])
                    hoteles["Direccion"].append(contacto_info)
                else:
                    hoteles["Direccion"].append("Información de contacto no encontrada")

                # Servicos
                services_list = []
                categories = soup2.find_all('div', class_='float-left mb-4 w-4/12')
                for category in categories:
                    services = [li.text for li in category.find_all('li')]
                    services_list.extend(services)
                hoteles["Servicios"].append(services_list)

                # Imprimir los servicios de los hoteles
                #for index, servicio in enumerate(hoteles["Servicios"]):
                    #print(f"Hotel {index + 1} - Servicios: {servicio}")

                time.sleep(3)

                # Cerrar  info
                cerrar_boton = navegador.find_element(By.CSS_SELECTOR,"button.SlideoutButton_slideoutButton__xb5Tt[data-testid='slideout-close']")
                cerrar_boton.click()
                time.sleep(2)

            # Mensaje de error al no hacer click en el boton
            except Exception as e:
                print(f"Error al hacer clic en el botón: {e}")
                continue

        # Boton de siguiente pagina
        if num_repeticiones is i+1:
            break
        else:
            boton_siguiente = navegador.find_element(By.XPATH, '//button[@data-testid="next-result-page"]')
            boton_siguiente.click()
            time.sleep(5)


    # Imprimir la longitud de cada lista
        for key, value in hoteles.items():
            print(f"Longitud de {key}: {len(value)}")

    # Encontrar la longitud máxima
    max_length = max(len(lst) for lst in hoteles.values())

    # Rellenar listas más cortas con None
    for key in hoteles:
        while len(hoteles[key]) < max_length:
            hoteles[key].append(None)

    # Crea el DataFrame y guarda los datos en un archivo CSV
    df = pd.DataFrame(hoteles)
    df.to_csv("C:/Users/sgoku/OneDrive/Escritorio/DatosClean/hoteles.csv", sep=";")
    print(df)

# Ejecucion del codigo
if __name__ == "__main__":
    navegador = configurar_navegador()
    try:
        navegar_y_buscar(navegador)
        extraer_datos(navegador, 1) # Numero de paginas que obtiene informacion
    finally:
        navegador.quit()