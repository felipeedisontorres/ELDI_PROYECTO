# Uso de inteligencia artificial (R-G08)

En el proyecto usamos Claude (de Anthropic) como tutor y co-diseñador. Le dimos los requisitos del curso, las
diapositivas y la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf`. El profesor nos autorizó a
usar código hecho con IA siempre que entendamos todo el código.

Le pusimos estas reglas: usar solo temas vistos en clase, citar el requisito que respalda cada propuesta, no
inventar datos ni números de pin, y explicarnos cada decisión con sus alternativas para poder entenderla y
defenderla.

## Para qué la usamos

| Etapa | Fechas | Para qué usamos la IA | ¿Generó código? |
|---|---|---|---|
| Elección y planteamiento | 14 al 27 de octubre | Comparar proyectos de la lista, ordenar los requisitos, analizar la guía del profesor y proponer alternativas para las primeras decisiones (D1 a D7) | No |
| Esquemático y código | 28 de octubre al 3 de noviembre | Dibujar el esquemático en una sola hoja y escribir los módulos, las pruebas y los pines a partir de él | Sí |
| Rediseños | 10 al 18 de noviembre | Simplificar el diseño con la retroalimentación del profesor (v3 y v4), cumplir los tiempos en Vivado (v4.1) y explicarnos cada bloque | Sí |
| Herramientas | 17 y 18 de noviembre | Ayudarnos a instalar Vivado y las librerías de Python, y escribir los scripts de Vivado y de Python | Sí |
| Prueba en la tarjeta | 23 de noviembre | Escribir el script de prueba y su versión corta para la demostración, ayudarnos a programar la tarjeta y encontrar por qué la primera imagen llegaba corrida un byte (D37) | Sí |
| Repositorio final | 24 de noviembre | Organizar el repositorio y redactar el README y los documentos | No |

## Qué hicimos nosotros y qué hizo la IA

**Nosotros:**
- Escogimos el proyecto, la tarjeta y qué tan complejo hacerlo.
- Presentamos los avances y trajimos la retroalimentación del profesor (R-F01, R-F02 y R-F03), que es la que
  llevó a cada rediseño.
- Escogimos entre las alternativas en las decisiones de diseño, por ejemplo de D1 a D7 y la D37 (ver
  [`docs/03_decisiones.md`](docs/03_decisiones.md)).
- Manejamos la tarjeta en la prueba (interruptores, botones e imágenes).
- Estudiamos el diseño bloque por bloque para la sustentación.
- Generar el cidigo a partir de la presenctacion, tematicas vistas en clase  y ayuda de la IA
- 

**La IA:**
- Propuso alternativas para las decisiones y nos explicó cada bloque con ejemplos.
- : los módulos de `rtl/`, las pruebas de `tb/`, los scripts de
  `sim/`, `python/` y `vivado/`, y los pines de `constraints/`, 
-  redactó la explicación bloque por bloque
-  Subió simulaciones y archivos al repositorio
-  Corrigió errores de código dentro de viviado

## Cómo se comprobó el código

- Cada módulo tiene su testbench y todos terminan en PASS.
- El sistema completo, simulado con la imagen de 128 × 128, da exactamente los mismos bytes que un modelo de
  referencia en los cinco modos.
- En la tarjeta, el 23 de noviembre, los cinco modos devolvieron exactamente los bytes esperados.

El detalle está en [`docs/04_verificacion.md`](docs/04_verificacion.md).
