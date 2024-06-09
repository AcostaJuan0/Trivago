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
        print(f"Repeticion {i+1}/{num_repeticiones}")

        # HTML de la página
        soup = BeautifulSoup(navegador.page_source, "html5lib")

        # Cuadros en los que se dividen los hoteles
        hotel_elementos = soup.find_all("li", {"data-testid": "accommodation-list-element"})

        # Ciclo en donde se obtienen los elementos y se agregan al diccionario
        for hotel_element in hotel_elementos:
            # Extraer nombres
            hotel_nombre = hotel_element.find("span", {"itemprop": "name"})
            # Limpiar y agregar el nombre del hotel al df
            if hotel_nombre is not None:
                nombre = hotel_nombre.get("title") or hotel_nombre.text
                hoteles["Nombre"].append(nombre)
            else:
                hoteles["Nombre"].append("Sin nombre")

            # Extraer numero de estrellas
            numero_estrelllas = hotel_element.find_all("span", {"data-testid": "star"})
            # Limpiar y agregar las estrellas al df
            if numero_estrelllas is not None:                        
                contar_estrellas = len(numero_estrelllas)
                estrellas = int(contar_estrellas)           
                hoteles["Estrellas"].append(estrellas)
            else:
                hoteles["Estrellas"].append(0)

            # Extraer nombre de la ciudad
            nombre_ciudad = hotel_element.find("span", {"class": "block text-left w-11/12 text-m"})
            # Limpiar y agregar el nombre de la ciudad al df
            if nombre_ciudad is not None:
                ciudad = nombre_ciudad.text
                hoteles["Ciudad"].append(ciudad)
            else:
                hoteles["Ciudad"].append("Sin Ciudad")

            # Extraer calificación del hotel
            hotel_calificacion = hotel_element.find("span", {"itemprop": "ratingValue"})
            # Limpiar y agregar la calificacion del hotel al df
            if hotel_calificacion is not None:
                cali = hotel_calificacion.text
                calificacion = float(cali)
                hoteles["Calificacion"].append(calificacion)
            else:
                hoteles["Calificacion"].append(0)

            # Extraer numero de resenas
            resenas_numero = hotel_element.find("meta", {"itemprop": "ratingCount"})
            # Limpiar y agregar el numero de resenas del hotel al df
            if resenas_numero is not None:
                rese = resenas_numero["content"]
                resenas = int(rese)                             
                hoteles["Numero de reseñas"].append(resenas)
            else:
                hoteles["Numero de reseñas"].append(0)

            try:
                # Extraer el precio por noche 
                hotel_precio = hotel_element.find("span", {"data-testid": "recommended-price"})
                # Limpiar y agregar el precio por noche del hotel al df
                if hotel_precio is not None:
                    pre = hotel_precio.text
                    precio = pre.lstrip("$")
                else:
                    precio = 0
            except Exception as e:
                print(f"Error al obtener el precio: {e}")
                precio = 0
            precio = int(precio)
            hoteles["Precio por noche"].append(precio)

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

                # Extraer elementos de Dirección
                direcciones = soup2.find("address", {"data-testid": "info-slideout-map-address"})
                ul = direcciones.find("ul", {"itemtype": "https://schema.org/PostalAddress"})
                if ul:
                    li_elementos = ul.find_all("li")
                    contacto_info = " ".join([li.text for li in li_elementos])
                    hoteles["Direccion"].append(contacto_info)
                else:
                    hoteles["Direccion"].append("Sin Información de contacto")

                # Servicos
                lista = []
                categoria = soup2.find_all('div', class_='float-left mb-4 w-4/12')
                for indice in categoria:
                    services = [li.text for li in indice.find_all('li')]
                    lista.extend(services)
                hoteles["Servicios"].append(lista)

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
    df.to_csv("C:/Users/Felip/OneDrive/Escritorio/DataFrame/hoteles.csv", sep=";")
    df.to_csv("Carpeta1/hoteles.csv", sep=";")
    print(df)

# Ejecucion del codigo
if __name__ == "__main__":
    navegador = configurar_navegador()
    try:
        navegar_y_buscar(navegador)
        extraer_datos(navegador, 9) # Numero de paginas que obtiene informacion
    finally:
        navegador.quit()