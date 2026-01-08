# 🎯 GUÍA DE SUSTENTACIÓN - EXAMEN II UNIDAD
## API REST en Go - Sistemas Distribuidos 2025

---

## ⚡ RESPUESTAS RÁPIDAS - LO MÁS IMPORTANTE

### 1. ¿QUÉ HICISTE EN EL PROYECTO?
**Respuesta corta:**
"Desarrollé una API REST en Go para un sistema de logs de auditoría con operaciones CRUD completas, implementando validaciones, manejo de errores HTTP y un frontend web que consume la API."

**Respuesta completa:**
- API de Logs de Auditoría en Go puerto 8010
- CRUD completo (Create, Read, Update, Delete)
- Validación de campos requeridos (accion y recurso)
- Frontend HTML/CSS/JavaScript conectado con CORS
- Almacenamiento en memoria con slices
- Manejo de códigos HTTP estándar

---

## 📚 PARTE 1: CONCEPTOS TEÓRICOS

### ¿Qué es una API REST?
**REST = Representational State Transfer**

Es un estilo arquitectónico para crear servicios web que usa:
- **HTTP como protocolo**
- **URLs para identificar recursos** (`/api/v1/logs`)
- **Métodos HTTP estándar** (GET, POST, PUT, DELETE)
- **JSON para intercambio de datos**
- **Stateless** (sin estado entre peticiones)

**Ejemplo real:**
```
GET /api/v1/logs/1  →  Obtener log con ID 1
POST /api/v1/logs   →  Crear nuevo log
```

---

### Principios REST (Los 5 principales)

| Principio | Explicación | Ejemplo |
|-----------|-------------|---------|
| **Stateless** | Cada petición es independiente, contiene toda la info necesaria | No hay sesiones en el servidor |
| **Client-Server** | Separación entre frontend y backend | HTML separado de API Go |
| **Cacheable** | Las respuestas pueden guardarse temporalmente | Headers Cache-Control |
| **Uniform Interface** | Interfaz consistente y predecible | Siempre uso `/api/v1/recurso` |
| **Layered System** | Arquitectura en capas | Puedo agregar balanceadores |

---

### Métodos HTTP - CRUD

| Método | Operación | Idempotente | Código Éxito | Tu Ejemplo |
|--------|-----------|-------------|--------------|------------|
| **GET** | Leer | ✅ SÍ | 200 | `GET /api/v1/logs` |
| **POST** | Crear | ❌ NO | 201 | `POST /api/v1/logs` |
| **PUT** | Actualizar completo | ✅ SÍ | 200 | `PUT /api/v1/logs/1` |
| **DELETE** | Eliminar | ✅ SÍ | 204 | `DELETE /api/v1/logs/1` |

**Idempotente significa:** Llamarlo N veces = mismo resultado que llamarlo 1 vez

**Ejemplo:**
- `GET /logs/1` → Llamar 10 veces devuelve el mismo log
- `DELETE /logs/1` → Llamar 10 veces: 1ra elimina, las demás dan 404 (resultado final = eliminado)
- `POST /logs` → Llamar 10 veces crea 10 logs diferentes ❌

---

### Códigos de Estado HTTP

#### 2xx - Éxito
- **200 OK** - GET o PUT exitoso
- **201 Created** - POST exitoso, recurso creado
- **204 No Content** - DELETE exitoso, sin respuesta

#### 4xx - Errores del Cliente
- **400 Bad Request** - JSON inválido o falta campo requerido
- **404 Not Found** - Recurso no existe
- **422 Unprocessable Entity** - Validación falló

#### 5xx - Errores del Servidor
- **500 Internal Server Error** - Error no manejado del servidor

---

## 💻 PARTE 2: TU CÓDIGO - EXPLICACIÓN LÍNEA POR LÍNEA

### Estructura del main.go (5 secciones)

```go
1. IMPORTS
2. MODELO (struct)
3. BASE DE DATOS (variables globales)
4. FUNCIONES AUXILIARES
5. HANDLERS (funciones HTTP)
6. MAIN (configuración)
```

---

### 1. IMPORTS - ¿Para qué sirve cada uno?

```go
import (
    "encoding/json"           // ✅ Convertir Go ↔ JSON
    "fmt"                     // ✅ Imprimir en consola
    "net/http"                // ✅ Servidor HTTP
    "strconv"                 // ✅ Convertir string → número (el ID)
    "time"                    // ✅ Timestamps automáticos
    "github.com/gorilla/mux"  // ✅ Router con variables en URL
)
```

**Pregunta típica:** ¿Por qué Gorilla Mux y no el router estándar?
**Respuesta:**
- Extrae variables de URL fácilmente: `{id}`
- Especifica métodos por ruta: `.Methods("GET")`
- Código más limpio y mantenible

---

### 2. MODELO - Struct con Tags JSON

```go
type AuditLog struct {
    ID        int       `json:"id"`
    Accion    string    `json:"accion"`    // requerido
    Recurso   string    `json:"recurso"`   // requerido
    UserID    int       `json:"user_id"`
    CreatedAt time.Time `json:"created_at"`
}
```

**¿Qué son los backticks `json:"id"`?**
- Son **tags de JSON**
- En Go: `ID` (mayúscula)
- En JSON: `"id"` (minúscula)
- Convierte automáticamente al codificar/decodificar

**Campos:**
- **Requeridos:** accion, recurso (validados en POST)
- **Opcionales:** user_id
- **Auto-generados:** id, created_at

---

### 3. BASE DE DATOS - Almacenamiento en Memoria

```go
var logs []AuditLog      // Slice que guarda todos los logs
var ultimoID int = 0     // Contador para IDs únicos
```

**¿Por qué slice y no base de datos real?**
- Propósito **educativo**
- Simple para aprender CRUD y HTTP
- En producción: PostgreSQL, MySQL, MongoDB

**¿Qué pasa al detener el servidor?**
- ❌ Los datos se PIERDEN (solo en RAM)

---

### 4. FUNCIONES AUXILIARES

#### buscarPorID()
```go
func buscarPorID(id int) (*AuditLog, int) {
    for i, log := range logs {
        if log.ID == id {
            return &logs[i], i
        }
    }
    return nil, -1
}
```

**Retorna 2 valores:**
1. Puntero al log encontrado (o `nil`)
2. Índice en el slice (o `-1`)

**¿Para qué?** Sirve para GET, PUT y DELETE

---

#### responderJSON()
```go
func responderJSON(w http.ResponseWriter, data interface{}, status int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}
```

**¿Para qué?** Evita repetir código. Centraliza el envío de respuestas JSON.

---

#### responderError()
```go
func responderError(w http.ResponseWriter, mensaje string, status int) {
    responderJSON(w, map[string]string{"error": mensaje}, status)
}
```

**Estandariza errores:** Todos se envían como `{"error": "mensaje"}`

---

### 5. HANDLERS - Las 6 funciones HTTP

#### GET /health
```go
func healthHandler(w http.ResponseWriter, r *http.Request) {
    responderJSON(w, map[string]string{
        "status":  "ok",
        "service": "api-logs",
    }, 200)
}
```

**¿Para qué?** Verificar que el servidor está funcionando

---

#### GET /api/v1/logs - Listar todos
```go
func listarLogs(w http.ResponseWriter, r *http.Request) {
    responderJSON(w, logs, 200)
}
```

**¿Qué devuelve si no hay logs?** Array vacío `[]` (no es error)

---

#### GET /api/v1/logs/{id} - Obtener uno
```go
func obtenerLog(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)                    // 1. Extraer variables URL
    id, err := strconv.Atoi(vars["id"])    // 2. Convertir string→int
    if err != nil {
        responderError(w, "ID inválido", 400)
        return
    }

    log, _ := buscarPorID(id)              // 3. Buscar en el slice
    if log == nil {
        responderError(w, "No encontrado", 404)
        return
    }

    responderJSON(w, log, 200)             // 4. Responder
}
```

**Códigos HTTP usados:**
- 400: ID no es número
- 404: ID válido pero no existe
- 200: Encontrado

---

#### POST /api/v1/logs - Crear
```go
func crearLog(w http.ResponseWriter, r *http.Request) {
    var nuevo AuditLog

    // 1. Decodificar JSON
    err := json.NewDecoder(r.Body).Decode(&nuevo)
    if err != nil {
        responderError(w, "JSON inválido", 400)
        return
    }

    // 2. Validar campos requeridos
    if nuevo.Accion == "" {
        responderError(w, "El campo 'accion' es requerido", 400)
        return
    }
    if nuevo.Recurso == "" {
        responderError(w, "El campo 'recurso' es requerido", 400)
        return
    }

    // 3. Asignar ID y fecha
    ultimoID++
    nuevo.ID = ultimoID
    nuevo.CreatedAt = time.Now()

    // 4. Guardar
    logs = append(logs, nuevo)

    // 5. Responder
    responderJSON(w, nuevo, 201)
}
```

**Validaciones implementadas:**
1. JSON válido
2. Campo 'accion' no vacío
3. Campo 'recurso' no vacío

**¿Por qué 201 y no 200?**
- 201 = Created (más semántico para POST)

**¿Qué hace `time.Now()`?**
- Genera timestamp automático de cuándo se creó

---

#### PUT /api/v1/logs/{id} - Actualizar
```go
func actualizarLog(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        responderError(w, "ID inválido", 400)
        return
    }

    log, index := buscarPorID(id)
    if log == nil {
        responderError(w, "No encontrado", 404)
        return
    }

    var actualizado AuditLog
    err = json.NewDecoder(r.Body).Decode(&actualizado)
    if err != nil {
        responderError(w, "JSON inválido", 400)
        return
    }

    // Mantener ID y fecha original
    actualizado.ID = id
    actualizado.CreatedAt = log.CreatedAt

    logs[index] = actualizado
    responderJSON(w, actualizado, 200)
}
```

**¿Por qué mantener `created_at` original?**
- Representa cuándo se CREÓ, no cuándo se modificó
- En producción: agregaríamos `updated_at`

**Diferencia POST vs PUT:**
- POST: Crea NUEVO recurso (genera ID)
- PUT: Actualiza recurso EXISTENTE (usa ID que ya existe)

---

#### DELETE /api/v1/logs/{id} - Eliminar
```go
func eliminarLog(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id, err := strconv.Atoi(vars["id"])
    if err != nil {
        responderError(w, "ID inválido", 400)
        return
    }

    _, index := buscarPorID(id)
    if index == -1 {
        responderError(w, "No encontrado", 404)
        return
    }

    // Eliminar del slice
    logs = append(logs[:index], logs[index+1:]...)

    w.WriteHeader(204) // No Content
}
```

**¿Cómo funciona la eliminación?**
```go
logs = append(logs[:index], logs[index+1:]...)
```
- `logs[:index]` = Todo ANTES del elemento
- `logs[index+1:]` = Todo DESPUÉS del elemento
- `append()` = Une ambas partes

**¿Por qué 204?**
- No Content = Exitoso pero sin datos que devolver

---

### 6. MAIN - Configuración

```go
func main() {
    router := mux.NewRouter()

    // Rutas
    router.HandleFunc("/health", healthHandler).Methods("GET")
    router.HandleFunc("/api/v1/logs", listarLogs).Methods("GET")
    router.HandleFunc("/api/v1/logs/{id}", obtenerLog).Methods("GET")
    router.HandleFunc("/api/v1/logs", crearLog).Methods("POST")
    router.HandleFunc("/api/v1/logs/{id}", actualizarLog).Methods("PUT")
    router.HandleFunc("/api/v1/logs/{id}", eliminarLog).Methods("DELETE")

    puerto := ":8010"

    // Mensajes
    fmt.Println("================================")
    fmt.Println("API iniciada en puerto", puerto)
    fmt.Println("================================")

    // Iniciar servidor
    http.ListenAndServe(puerto, enableCORS(router))
}
```

**¿Qué hace el router?**
Mapea URLs → Funciones
- Compara URL y método HTTP
- Ejecuta la función correspondiente
- Extrae variables `{id}`

**¿Por qué la misma ruta `/api/v1/logs` tiene 2 handlers?**
Se diferencian por el MÉTODO:
- GET → listarLogs()
- POST → crearLog()

**¿Qué hace `http.ListenAndServe()`?**
Inicia el servidor en puerto 8010 y espera peticiones

---

## 🔧 PARTE 3: CORS - Cross-Origin Resource Sharing

### ¿Qué es CORS?
Permite que un **frontend en un dominio** (ej: `localhost:5500`) pueda hacer peticiones a una **API en otro dominio** (ej: `localhost:8010`)

### ¿Por qué se necesita?
Los navegadores bloquean peticiones entre dominios por seguridad. CORS permite autorizarlas.

### Implementación en tu código

```go
func enableCORS(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Headers CORS
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

        // Preflight request
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }

        next.ServeHTTP(w, r)
    })
}
```

**¿Qué hace cada header?**
- `Allow-Origin: *` → Acepta peticiones de cualquier dominio
- `Allow-Methods` → Métodos HTTP permitidos
- `Allow-Headers` → Headers permitidos en la petición

**¿Qué es preflight request?**
Antes de POST/PUT/DELETE, el navegador envía OPTIONS para verificar permisos

---

## 🖥️ PARTE 4: FRONTEND

### Características de tu index.html

1. **Verificación de estado API** (badge online/offline)
2. **Estadísticas en tiempo real**
   - Total logs
   - Logs de hoy
   - Logs del último minuto
3. **Formulario crear log** (accion, recurso, user_id)
4. **Búsqueda por ID**
5. **Filtrado por texto** (accion o recurso)
6. **Lista visual de logs**
7. **Auto-refresh cada 10 segundos**
8. **Atajo: Ctrl+Enter para crear**

### Código clave del frontend

```javascript
const API = 'http://localhost:8010/api/v1/logs';

// Crear log
async function crear() {
    const accion = document.getElementById('accion').value.trim();
    const recurso = document.getElementById('recurso').value.trim();
    const user_id = document.getElementById('user_id').value;

    const body = { accion, recurso };
    if (user_id) body.user_id = parseInt(user_id);

    const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        cargar();
        alert('✅ Log creado');
    }
}
```

**¿Cómo se conecta frontend con backend?**
- `fetch(API)` hace peticiones HTTP
- `async/await` para manejar promesas
- `JSON.stringify()` convierte objeto → JSON
- `res.json()` convierte respuesta JSON → objeto

---

## 🧪 PARTE 5: PRUEBAS CON CURL

### Verificar servidor
```bash
curl http://localhost:8010/health
```
**Respuesta esperada:**
```json
{"status":"ok","service":"api-logs"}
```

---

### Crear log
```bash
curl -X POST http://localhost:8010/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "accion": "CREATE",
    "recurso": "users",
    "user_id": 1
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": 1,
  "accion": "CREATE",
  "recurso": "users",
  "user_id": 1,
  "created_at": "2025-01-08T10:30:45.123Z"
}
```

---

### Listar todos
```bash
curl http://localhost:8010/api/v1/logs
```

---

### Obtener por ID
```bash
curl http://localhost:8010/api/v1/logs/1
```

---

### Actualizar
```bash
curl -X PUT http://localhost:8010/api/v1/logs/1 \
  -H "Content-Type: application/json" \
  -d '{
    "accion": "UPDATE",
    "recurso": "products",
    "user_id": 2
  }'
```

---

### Eliminar
```bash
curl -X DELETE http://localhost:8010/api/v1/logs/1
```
**Respuesta:** 204 No Content (sin cuerpo)

---

### Probar validación (error)
```bash
curl -X POST http://localhost:8010/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Respuesta (400):**
```json
{"error":"El campo 'accion' es requerido"}
```

---

## 📊 PARTE 6: TABLA RESUMEN CRUD

| Operación | Método | Endpoint | Código Éxito | Cuerpo Petición | Qué hace |
|-----------|--------|----------|--------------|-----------------|----------|
| Crear | POST | `/api/v1/logs` | 201 | JSON con accion, recurso | Crea nuevo log |
| Listar | GET | `/api/v1/logs` | 200 | - | Devuelve array de logs |
| Obtener | GET | `/api/v1/logs/1` | 200 | - | Devuelve log con ID 1 |
| Actualizar | PUT | `/api/v1/logs/1` | 200 | JSON con datos nuevos | Actualiza log 1 |
| Eliminar | DELETE | `/api/v1/logs/1` | 204 | - | Elimina log 1 |
| Health | GET | `/health` | 200 | - | Verifica servidor |

---

## 🎤 PARTE 7: PREGUNTAS TÍPICAS DEL DOCENTE

### 1. ¿Por qué usaste Go?
**Respuesta:**
- Compilado y rápido
- Concurrencia nativa (goroutines)
- Sintaxis simple
- Biblioteca estándar potente para HTTP
- Popular en sistemas distribuidos

---

### 2. ¿Qué es un Handler en Go?
**Respuesta:**
Una función que recibe una petición HTTP y genera una respuesta. Tiene la firma:
```go
func(w http.ResponseWriter, r *http.Request)
```
- `w` = Para escribir la respuesta
- `r` = Contiene datos de la petición

---

### 3. ¿Diferencia entre PUT y PATCH?
**Respuesta:**
- **PUT:** Reemplaza el recurso COMPLETO
- **PATCH:** Actualiza solo campos específicos
- En tu API usas PUT (reemplaza todo el log)

---

### 4. ¿Qué mejoras harías en producción?
**Respuesta:**
1. Base de datos real (PostgreSQL)
2. Autenticación JWT
3. Logging estructurado
4. Tests unitarios
5. Paginación
6. Rate limiting
7. Documentación OpenAPI/Swagger
8. Validación con librerías (validator)
9. Manejo de concurrencia con mutex
10. Docker para deployment

---

### 5. ¿Cómo manejas la concurrencia?
**Respuesta:**
Actualmente NO manejo concurrencia explícita. En producción usaría:
```go
var (
    logs []AuditLog
    mu   sync.RWMutex
)

func crearLog() {
    mu.Lock()           // Bloquear para escritura
    defer mu.Unlock()
    logs = append(logs, nuevo)
}

func listarLogs() {
    mu.RLock()          // Bloquear para lectura
    defer mu.RUnlock()
    return logs
}
```

---

### 6. ¿Qué es un middleware?
**Respuesta:**
Función que se ejecuta ANTES de los handlers. Ejemplo: CORS

```
Request → enableCORS() → handler → Response
```

Útil para: logging, autenticación, CORS, etc.

---

### 7. ¿Por qué JSON y no XML?
**Respuesta:**
- Más ligero (menos caracteres)
- Más fácil de leer
- Nativo en JavaScript
- Estándar actual de APIs REST

---

### 8. ¿Qué es una API RESTful?
**Respuesta:**
API que cumple los principios REST:
- Usa métodos HTTP semánticos
- URLs representan recursos
- Stateless
- Usa códigos HTTP apropiados

---

### 9. ¿Por qué almacenamiento en memoria?
**Respuesta:**
Propósito educativo para:
- Enfocarse en HTTP y REST
- Evitar complejidad de BD
- Prototipar rápido

Desventajas:
- Datos se pierden al reiniciar
- No escala

---

### 10. ¿Cómo probarías la API?
**Respuesta:**
1. **Manual:** curl, Postman
2. **Tests unitarios:** Go testing
3. **Tests integración:** Tabla de casos
4. **Frontend:** Navegador

---

## 🔥 PARTE 8: FLUJO COMPLETO DE UNA PETICIÓN POST

```
1. Cliente (curl/frontend) envía JSON
   ↓
2. Servidor recibe en puerto 8010
   ↓
3. Middleware CORS agrega headers
   ↓
4. Router busca ruta `/api/v1/logs` + método POST
   ↓
5. Ejecuta handler crearLog()
   ↓
6. Decodifica JSON → struct AuditLog
   ↓
7. Valida campos requeridos
   ↓
8. Genera ID (ultimoID++)
   ↓
9. Genera timestamp (time.Now())
   ↓
10. Agrega al slice
   ↓
11. Codifica struct → JSON
   ↓
12. Envía respuesta 201 Created
```

---

## 💡 PARTE 9: CONSEJOS PARA LA SUSTENTACIÓN

### ✅ HAZ ESTO:

1. **Arranca el servidor ANTES** de presentar
2. **Ten curl listo** en una terminal
3. **Abre el frontend en navegador**
4. **Explica mientras demuestras** (habla y muestra código)
5. **Usa las manos** para señalar código importante
6. **Di los códigos HTTP** en voz alta (201, 404, etc.)
7. **Muestra errores** (validación) para demostrar robustez

### ❌ NO HAGAS ESTO:

1. NO leas el código como loro
2. NO te quedes callado
3. NO digas "no sé" (di "déjame verificar")
4. NO improvises funciones que no existen
5. NO te pongas nervioso si falla algo (arréglalo en vivo)

---

## 🎯 PARTE 10: DEMOSTRACIÓN EN VIVO - SCRIPT

### Orden recomendado:

**1. Mostrar código (2 min)**
```
"Desarrollé una API REST en Go con 6 endpoints CRUD..."
[Mostrar estructura de archivos]
"La estructura sigue 5 secciones: modelo, base de datos, auxiliares, handlers y main"
```

**2. Arrancar servidor (30 seg)**
```bash
cd apis-rest-puro-ia
go run main.go
```
```
"Como pueden ver, el servidor arranca en puerto 8010 con 6 endpoints"
```

**3. Health check (30 seg)**
```bash
curl http://localhost:8010/health
```
```
"Primero verifico que el servidor responde correctamente"
```

**4. Crear logs (1 min)**
```bash
curl -X POST http://localhost:8010/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{"accion":"CREATE","recurso":"users","user_id":1}'
```
```
"Al crear un log, el servidor valida campos requeridos, genera ID automático y timestamp"
```

**5. Listar (30 seg)**
```bash
curl http://localhost:8010/api/v1/logs
```
```
"Aquí vemos el log que acabo de crear en el array"
```

**6. Obtener por ID (30 seg)**
```bash
curl http://localhost:8010/api/v1/logs/1
```

**7. Mostrar frontend (1 min)**
```
[Abrir index.html en navegador]
"El frontend consume la API mediante fetch y muestra estadísticas en tiempo real"
[Crear un log desde el formulario]
```

**8. Mostrar validación (30 seg)**
```bash
curl -X POST http://localhost:8010/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{}'
```
```
"Al enviar datos incompletos, el servidor responde 400 Bad Request con mensaje descriptivo"
```

**9. Eliminar (30 seg)**
```bash
curl -X DELETE http://localhost:8010/api/v1/logs/1
```
```
"DELETE responde 204 No Content indicando éxito sin cuerpo de respuesta"
```

**10. Cerrar**
```
"La API implementa los principios REST, usa códigos HTTP apropiados y tiene manejo de errores robusto"
```

---

## 📝 PARTE 11: CHEAT SHEET - RESPUESTAS DE 1 LÍNEA

| Pregunta | Respuesta Ultra-Corta |
|----------|----------------------|
| ¿Qué es REST? | Estilo arquitectónico para APIs usando HTTP, URLs y JSON |
| ¿Qué es CRUD? | Create Read Update Delete - operaciones básicas |
| ¿Qué hace GET? | Lee/obtiene recursos sin modificar |
| ¿Qué hace POST? | Crea nuevos recursos |
| ¿Qué hace PUT? | Actualiza recursos existentes completamente |
| ¿Qué hace DELETE? | Elimina recursos |
| ¿Qué es idempotente? | Llamar N veces = mismo resultado que 1 vez |
| ¿Qué es 201? | Created - recurso creado exitosamente |
| ¿Qué es 404? | Not Found - recurso no existe |
| ¿Qué es 400? | Bad Request - datos inválidos |
| ¿Para qué CORS? | Permitir peticiones entre diferentes dominios |
| ¿Para qué Gorilla Mux? | Router con variables en URL y métodos por ruta |
| ¿Qué es handler? | Función que procesa peticiones HTTP |
| ¿Por qué en memoria? | Simplicidad educativa, en producción uso BD |
| ¿Qué es JSON? | Formato de intercambio de datos ligero |

---

## 🚀 PARTE 12: COMANDOS ESENCIALES

### Arrancar API
```bash
cd apis-rest-puro-ia
go run main.go
```

### Verificar salud
```bash
curl http://localhost:8010/health
```

### Crear log
```bash
curl -X POST http://localhost:8010/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{"accion":"CREATE","recurso":"users","user_id":1}'
```

### Listar logs
```bash
curl http://localhost:8010/api/v1/logs
```

### Obtener log
```bash
curl http://localhost:8010/api/v1/logs/1
```

### Actualizar log
```bash
curl -X PUT http://localhost:8010/api/v1/logs/1 \
  -H "Content-Type: application/json" \
  -d '{"accion":"UPDATE","recurso":"products","user_id":2}'
```

### Eliminar log
```bash
curl -X DELETE http://localhost:8010/api/v1/logs/1
```

### Abrir frontend
```bash
# Desde el navegador abrir:
file:///home/.../ultimo/api-frontend-puro-ia/index.html
```

---

## ✨ PARTE 13: PALABRAS CLAVE PARA IMPRESIONAR

Usa estos términos durante la sustentación:

1. **"Implementé operaciones CRUD completas"**
2. **"Siguiendo principios REST"**
3. **"Con validación de campos requeridos"**
4. **"Manejo apropiado de códigos HTTP"**
5. **"Middleware CORS para comunicación cross-origin"**
6. **"Almacenamiento en memoria con slices"**
7. **"Serialización JSON bidireccional"**
8. **"Extracción de parámetros de ruta"**
9. **"Respuestas estandarizadas"**
10. **"Frontend reactivo con fetch API"**

---

## 🎓 PARTE 14: ESTRUCTURA DE RESPUESTA PERFECTA

### Formato recomendado para responder:

1. **Respuesta directa** (1 frase)
2. **Ejemplo de tu código** (señala archivo)
3. **Demostración** (si aplica)

**Ejemplo:**

**Pregunta:** ¿Qué es un handler?

**Respuesta:**
"Un handler es una función que procesa peticiones HTTP" ← [DIRECTO]

"En mi código, crearLog() es un handler que recibe la petición POST, valida datos, genera ID y devuelve 201" ← [EJEMPLO]

[Señalar función en pantalla] ← [DEMOSTRACIÓN]

---

## ⏰ TIMING SUGERIDO (10 minutos total)

- **0-1 min:** Introducción del proyecto
- **1-3 min:** Explicar estructura del código
- **3-6 min:** Demostración en vivo (curl + frontend)
- **6-8 min:** Preguntas del docente
- **8-10 min:** Conceptos teóricos REST

---

## 🏆 CHECKLIST PRE-EXAMEN

Antes de entrar:

- [ ] Servidor corriendo: `go run main.go`
- [ ] Terminal con curl lista
- [ ] Frontend abierto en navegador
- [ ] Editor con main.go visible
- [ ] Esta guía abierta en otra ventana
- [ ] Agua para la garganta
- [ ] Respira profundo

---

## 💪 MENSAJE FINAL

**TÚ PUEDES HACERLO**

Ya tienes:
- ✅ Código funcional
- ✅ Documentación completa
- ✅ Esta guía de estudio
- ✅ Ejemplos de demostración

**Estrategia:**
1. Habla con CONFIANZA
2. Muestra el código FUNCIONANDO
3. Explica el "POR QUÉ" de cada decisión
4. Si no sabes algo, di "Es una mejora que implementaría"

**Recuerda:**
- El docente quiere que APRUEBES
- Está evaluando tu APRENDIZAJE, no perfección
- Es mejor decir "no lo implementé pero sé cómo hacerlo" que mentir

---

## 📞 ÚLTIMA AYUDA RÁPIDA

Si te preguntan algo que no recuerdas:

**Frase salvadora:**
"Déjame verificar en mi código... [buscas] ...aquí está, esto hace [explicas]"

---

# ¡ÉXITO EN TU EXAMEN! 🚀

**ÚLTIMO CONSEJO:** Lee esta guía 2 veces, practica la demostración 1 vez, y entra con confianza.

---

**Fecha:** 08/01/2025
**Curso:** Sistemas Distribuidos 2025
**Docente:** Alain Paul Herrera Urtiaga
**Tema:** API REST en Go - Sustentación II Unidad
