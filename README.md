# DevSecOps RBAC Platform

Plataforma empresarial para la **gestión centralizada de usuarios, empresas, aplicaciones, cargos, roles y permisos**, construida bajo una arquitectura de microservicios y orientada a prácticas **DevSecOps**.

El proyecto integra desarrollo de software, seguridad, automatización, control de acceso, trazabilidad, contenedores y CI/CD dentro de una plataforma diseñada para demostrar un flujo completo de desarrollo seguro.

---

## 📌 Descripción del proyecto

**DevSecOps RBAC Platform** es una plataforma de gestión de control de acceso basada en **RBAC (Role-Based Access Control)** y **multiempresa (multi-tenant)**.

Su objetivo es permitir que diferentes empresas administren de manera aislada:

- Usuarios.
- Empresas.
- Aplicaciones.
- Cargos.
- Roles.
- Permisos.
- Relaciones entre cargos, roles y permisos.
- Actividad y auditoría.
- Información proveniente de archivos Excel.
- Procesos de sincronización.

La plataforma está diseñada utilizando una arquitectura de **microservicios**, donde cada servicio tiene una responsabilidad específica y, cuando corresponde, su propia base de datos.

El proyecto también sirve como laboratorio práctico para implementar un ciclo DevSecOps que incorpore seguridad desde las primeras etapas del desarrollo.

---

# 🎯 Objetivos

## Objetivo general

Diseñar e implementar una plataforma RBAC multiempresa utilizando una arquitectura de microservicios y aplicando principios DevSecOps para integrar desarrollo, seguridad, pruebas, automatización y despliegue.

## Objetivos específicos

- Implementar autenticación centralizada.
- Implementar autorización basada en roles.
- Aislar la información entre empresas.
- Centralizar la gestión de usuarios.
- Gestionar aplicaciones, cargos, roles y permisos.
- Implementar trazabilidad y auditoría.
- Procesar información mediante archivos Excel.
- Utilizar contenedores Docker.
- Implementar comunicación entre servicios.
- Incorporar pruebas automatizadas.
- Integrar análisis de seguridad en el ciclo CI/CD.
- Aplicar SAST, SCA, análisis de secretos, seguridad de contenedores e infraestructura.
- Generar una arquitectura preparada para evolución hacia Kubernetes y cloud.
- Mantener una separación clara de responsabilidades entre servicios.

---

# 🏗️ Arquitectura

La solución utiliza una arquitectura basada en microservicios.

```text
                              ┌─────────────────────┐
                              │      Frontend       │
                              │   React + Vite      │
                              │     Port 5173       │
                              └──────────┬──────────┘
                                         │
                                         │ HTTP
                                         ▼
                              ┌─────────────────────┐
                              │    API Gateway      │
                              │     FastAPI         │
                              │     Port 8000       │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
          │ Identity Service │ │   RBAC Service   │ │  Audit Service   │
          │                  │ │                  │ │                  │
          │ Auth / Users     │ │ Apps / Positions │ │ Logs / Activity  │
          │ Companies        │ │ Permissions      │ │                  │
          └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
                   │                    │                    │
                   ▼                    ▼                    ▼
          ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
          │   Identity DB    │ │     RBAC DB      │ │    Audit DB      │
          │   PostgreSQL     │ │    PostgreSQL    │ │    PostgreSQL    │
          └──────────────────┘ └──────────────────┘ └──────────────────┘

                    ┌────────────────────┐
                    │   Sync Service     │
                    │   Excel Worker     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │      Sync DB       │
                    │     PostgreSQL     │
                    └────────────────────┘

                    ┌────────────────────┐
                    │     RabbitMQ       │
                    │ Message Broker     │
                    └────────────────────┘

                    ┌────────────────────┐
                    │       MinIO        │
                    │ Object Storage     │
                    └────────────────────┘
```

---

# 🧩 Componentes

## Frontend

Tecnologías:

- React 19
- Vite
- JavaScript
- CSS
- Node.js

Responsabilidades:

- Inicio de sesión.
- Manejo de sesión.
- Consulta del usuario autenticado.
- Dashboard.
- Visualización de módulos según el rol.
- Interacción con el API Gateway.
- Experiencia de usuario.

El frontend **no es la autoridad de seguridad**.

Ocultar una opción del menú no significa que el usuario tenga o no tenga permisos.

La autorización real debe ser aplicada en el backend.

---

# 🚪 API Gateway

El API Gateway constituye el punto de entrada HTTP de la plataforma.

Puerto:

```text
8000
```

Responsabilidades:

- Recibir solicitudes del frontend.
- Enrutar solicitudes hacia los microservicios.
- Centralizar el acceso HTTP.
- Manejar CORS.
- Mantener un punto de entrada único para el frontend.

Ejemplo:

```text
Frontend
   │
   ▼
http://localhost:8000
   │
   ├── /api/identity/*
   ├── /api/rbac/*
   ├── /api/audit/*
   └── /api/sync/*
```

---

# 🔐 Identity Service

Servicio responsable de identidad y autenticación.

Tecnologías principales:

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT
- OAuth2 Password Flow
- pwdlib

Responsabilidades:

- Usuarios.
- Empresas.
- Autenticación.
- Contraseñas.
- Roles base.
- Tokens JWT.
- Identidad del usuario autenticado.
- Asociación usuario ↔ empresa.

---

# 🔑 Modelo de autenticación

La plataforma utiliza un **único inicio de sesión**.

El usuario:

1. Introduce usuario y contraseña.
2. El Identity Service valida las credenciales.
3. El backend determina la empresa asociada al usuario.
4. Se genera un nuevo Access Token.
5. El frontend utiliza el token para consumir los servicios.
6. El backend valida el token en cada operación protegida.

### No existe selección manual de empresa

El usuario **no selecciona la empresa desde el login**.

La empresa se obtiene desde la identidad almacenada en el backend.

Esto evita que un usuario pueda intentar seleccionar manualmente otra empresa desde el frontend.

---

# 🎫 JWT

Los Access Tokens contienen información asociada al usuario autenticado.

Conceptualmente:

```json
{
  "sub": "1",
  "username": "admin",
  "role": "admin",
  "company_id": 1,
  "exp": "..."
}
```

El token tiene una duración corta.

Configuración actual:

```text
30 minutos
```

El objetivo es reducir el impacto de una eventual exposición del token.

---

# 🏢 Multi-tenancy

La plataforma utiliza un modelo multiempresa.

Actualmente existen:

```text
Empresa 1
Empresa 2
Empresa 3
```

Cada usuario empresarial está asociado a una empresa.

Ejemplo:

```text
Usuario
   │
   └── company_id = 1
              │
              ▼
          Empresa 1
```

La separación entre empresas debe ser aplicada por el backend.

## Principio fundamental

> El frontend puede ocultar funcionalidades, pero nunca debe ser considerado un mecanismo de seguridad.

La autorización y aislamiento deben ser comprobados en los servicios backend.

---

# 👥 Roles

Actualmente se manejan tres roles principales:

| Rol | Descripción |
|---|---|
| `superadmin` | Administración global de la plataforma |
| `admin` | Administración de una empresa |
| `user` | Usuario estándar |

---

## Superadmin

El `superadmin` opera a nivel global.

Puede:

- Gestionar empresas.
- Consultar empresas.
- Crear administradores.
- Crear usuarios.
- Administrar información global permitida.
- Acceder a funcionalidades administrativas globales.

El superadmin no pertenece obligatoriamente a una empresa.

Actualmente:

```text
company_id = NULL
```

---

## Admin

El administrador pertenece a una empresa específica.

Ejemplo:

```text
admin
   │
   └── Empresa 1
```

Puede:

- Gestionar usuarios de su empresa.
- Crear usuarios dentro de su empresa.
- Trabajar con funcionalidades autorizadas para su empresa.

No puede:

- Crear usuarios en otra empresa.
- Crear superadmins.
- Crear otros administradores.
- Administrar globalmente las empresas.

---

## User

Usuario estándar de una empresa.

Puede acceder únicamente a las funcionalidades que posteriormente sean autorizadas para su rol y permisos.

El usuario no debe poder modificar información administrativa de su empresa solamente mediante manipulación del frontend.

---

# 🔒 Autorización

El proyecto utiliza una arquitectura de autorización basada en roles.

Se implementaron dependencias backend para controlar privilegios.

Ejemplo conceptual:

```text
JWT
 │
 ▼
Usuario autenticado
 │
 ▼
Rol
 │
 ├── superadmin
 │
 ├── admin
 │
 └── user
```

Las restricciones importantes se validan en backend.

Por ejemplo:

```text
Admin Empresa 1
       │
       ├── Crear usuario Empresa 1 → permitido
       │
       ├── Crear usuario Empresa 2 → rechazado
       │
       ├── Crear otro admin → rechazado
       │
       └── Crear superadmin → rechazado
```

---

# 🗄️ Bases de datos

Cada dominio principal mantiene su propia base de datos.

Esto permite mantener separación de responsabilidades y reducir el acoplamiento entre microservicios.

| Servicio | Base de datos |
|---|---|
| Identity Service | Identity DB |
| RBAC Service | RBAC DB |
| Audit Service | Audit DB |
| Sync Service | Sync DB |

Motor utilizado:

```text
PostgreSQL
```

Versión utilizada en Docker Compose:

```text
postgres:17-alpine
```

---

# 🧱 RBAC Service

El RBAC Service administra la estructura relacionada con control de acceso.

Conceptualmente:

```text
Empresa
   │
   ▼
Aplicación
   │
   ▼
Cargo
   │
   ▼
Rol
   │
   ▼
Permiso
```

Actualmente existen endpoints para trabajar con:

- Applications
- Positions
- Permissions

El modelo continuará evolucionando para incorporar completamente:

- Roles.
- Asignación de roles.
- Asignación de permisos.
- Relaciones entre cargos y roles.
- Relaciones entre roles y permisos.
- Restricciones por empresa.

---

# 📋 Aplicaciones

Una aplicación representa un sistema o aplicación administrada por la plataforma.

Ejemplo:

```text
Nombre: Sistema Financiero
Código: FIN
```

El código permite identificar la aplicación de forma consistente.

---

# 💼 Cargos

Los cargos representan posiciones dentro de una empresa.

Ejemplo:

```text
Nombre: Analista de Seguridad
Código: SEC_ANALYST
Empresa: Empresa 1
```

El código del cargo debe ser único dentro de su empresa.

---

# 🛡️ Permisos

Los permisos representan acciones que un usuario puede realizar.

Ejemplos:

```text
CONSULTAR
CREAR
EDITAR
ELIMINAR
EXPORTAR
ADMINISTRAR
```

Ejemplo actualmente utilizado:

```json
{
  "name": "CONSULTAR",
  "detail": "Permite consultar información"
}
```

---

# 📊 Matriz RBAC

La matriz objetivo de autorización es:

```text
Empresa
   │
   ├── Aplicación
   │      │
   │      └── Cargo
   │             │
   │             └── Rol
   │                    │
   │                    └── Permiso
   │
   └── Usuarios
```

Esta estructura permitirá representar de forma centralizada qué puede hacer cada usuario dentro de una determinada empresa y aplicación.

---

# 📝 Audit Service

El Audit Service está destinado al registro de actividad de la plataforma.

Su objetivo es proporcionar trazabilidad sobre operaciones relevantes.

Eventos esperados:

- Inicio de sesión.
- Creación de usuarios.
- Modificación de usuarios.
- Eliminación o desactivación.
- Creación de empresas.
- Cambios de permisos.
- Importaciones.
- Exportaciones.
- Acciones administrativas.
- Errores relevantes.

Estructura conceptual:

```text
Usuario
   │
   ▼
Acción
   │
   ▼
Servicio
   │
   ▼
Resultado
   │
   ▼
Evento de auditoría
```

El servicio dispone actualmente de un endpoint para registrar eventos de auditoría.

Ejemplo conceptual:

```json
{
  "user_id": 1,
  "action": "CREATE_USER",
  "service": "identity-service",
  "status": "SUCCESS",
  "details": "Usuario creado"
}
```

---

# 📑 Excel Sync & Storage

El sistema contempla un servicio destinado al manejo de información proveniente de archivos Excel.

Objetivos:

- Importar información.
- Procesar archivos.
- Validar información.
- Sincronizar datos.
- Exportar información.
- Almacenar archivos.
- Gestionar procesos mediante un worker.

Componentes:

```text
Frontend
   │
   ▼
API Gateway
   │
   ▼
Sync Service
   │
   ├── Sync DB
   │
   ├── RabbitMQ
   │
   └── Excel Worker
             │
             ▼
           MinIO
```

---

# 📨 RabbitMQ

RabbitMQ funciona como broker de mensajes para permitir comunicación asíncrona entre componentes.

Su utilización permite separar procesos que no necesariamente deben ejecutarse dentro de la misma solicitud HTTP.

Ejemplo:

```text
Usuario
   │
   ▼
Importar Excel
   │
   ▼
Sync Service
   │
   ▼
RabbitMQ
   │
   ▼
Excel Worker
   │
   ▼
Procesamiento
```

Esto permite evolucionar posteriormente hacia procesos más escalables.

---

# 🗃️ MinIO

MinIO se utiliza como almacenamiento de objetos.

Su función dentro de la arquitectura está orientada principalmente a archivos relacionados con:

- Excel.
- Importaciones.
- Exportaciones.
- Archivos procesados.
- Evidencias o artefactos que requieran almacenamiento.

Arquitectura:

```text
Sync Service
     │
     ▼
   MinIO
     │
     ├── Archivos originales
     ├── Archivos procesados
     └── Exportaciones
```

---

# 🐳 Docker

La plataforma utiliza Docker para ejecutar los diferentes componentes de manera aislada.

Los servicios se administran mediante:

```text
docker compose
```

Los principales contenedores son:

```text
api-gateway
identity-service
identity-db
rbac-service
rbac-db
audit-service
audit-db
sync-service
sync-db
excel-worker
rabbitmq
minio
```

---

# 🚀 Requisitos

Para ejecutar el proyecto localmente se recomienda:

- Git
- Docker
- Docker Compose
- Node.js
- npm
- Python 3
- Linux, WSL o entorno compatible

Versiones utilizadas durante el desarrollo:

```text
Node.js 24.x
npm 11.x
Docker
Docker Compose
Python 3.x
PostgreSQL 17
```

Las versiones pueden evolucionar durante el desarrollo.

---

# 📥 Instalación

Clonar el repositorio:

```bash
git clone git@github.com:odesarrollo25/devsecops-rbac-platform.git
```

Ingresar al proyecto:

```bash
cd devsecops-rbac-platform
```

---

# 🐳 Levantar backend

Ejecutar:

```bash
docker compose up -d
```

Verificar los contenedores:

```bash
docker compose ps
```

Para reconstruir imágenes después de modificar código:

```bash
docker compose up -d --build
```

---

# 🔎 Verificación del API Gateway

Health check:

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "service": "api-gateway",
  "status": "healthy"
}
```

---

# 🔎 Verificación del Identity Service

```bash
curl http://localhost:8000/api/identity/health
```

---

# 🔎 Verificación del RBAC Service

```bash
curl http://localhost:8000/api/rbac/health
```

---

# 💻 Frontend

El frontend se encuentra en:

```text
frontend/
```

Instalar dependencias:

```bash
cd frontend
npm install
```

Iniciar servidor de desarrollo:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

API Gateway:

```text
http://localhost:8000
```

---

# 🔐 Configuración CORS

El API Gateway permite actualmente el origen de desarrollo:

```text
http://localhost:5173
```

Esto permite que el frontend React pueda comunicarse con el backend durante el desarrollo.

En producción, los orígenes permitidos deberán configurarse explícitamente según el dominio utilizado.

---

# 🔑 Usuarios de desarrollo

Los siguientes usuarios existen actualmente para pruebas:

| Usuario | Rol | Empresa | Propósito |
|---|---|---|---|
| `superadmin` | `superadmin` | Global / sin empresa | Administración global |
| `admin` | `admin` | Empresa 1 | Administración de Empresa 1 |
| `usuarioempresa1` | `user` | Empresa 1 | Usuario estándar |

## Contraseñas

Las contraseñas de desarrollo **no se almacenan en este README ni deben subirse al repositorio**.

Deben mantenerse localmente o mediante variables/secretos de entorno.

> ⚠️ Si estas credenciales se utilizan únicamente para desarrollo académico, deben cambiarse antes de cualquier despliegue real.

---

# 🧪 Pruebas de autenticación

El login utiliza:

```text
POST /api/identity/login
```

El endpoint utiliza `application/x-www-form-urlencoded`.

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=PASSWORD"
```

La respuesta contiene:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

# 👤 Usuario autenticado

Después del login:

```text
GET /api/identity/me
```

Con:

```text
Authorization: Bearer <TOKEN>
```

Ejemplo:

```bash
curl http://localhost:8000/api/identity/me \
  -H "Authorization: Bearer $TOKEN_ADMIN"
```

Respuesta conceptual:

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@devsecops.com",
  "full_name": "Administrator",
  "role": "admin",
  "company_id": 1,
  "company_name": "Empresa 1",
  "is_active": true
}
```

---

# 🏢 Gestión de empresas

El acceso a las empresas está restringido al superadmin.

Consultar empresas:

```text
GET /api/identity/companies
```

Crear empresa:

```text
POST /api/identity/companies
```

Un administrador empresarial no debe poder consultar ni modificar la administración global de empresas.

---

# 👤 Gestión de usuarios

Registrar usuario:

```text
POST /api/identity/register
```

El backend valida:

- Usuario existente.
- Email existente.
- Empresa existente.
- Empresa activa.
- Rol solicitado.
- Empresa del administrador.
- Privilegios del administrador.

Ejemplo de aislamiento:

```text
Admin Empresa 1
      │
      ├── Usuario Empresa 1 → permitido
      │
      └── Usuario Empresa 2 → HTTP 403
```

---

# 🧪 Pruebas de autorización realizadas

## Superadmin

Se verificó que:

```text
GET /api/identity/companies
```

con el token de superadmin devuelve:

```text
HTTP 200 OK
```

---

## Admin

Se verificó que un administrador intentando acceder al listado global de empresas recibe:

```text
HTTP 403 Forbidden
```

Respuesta:

```json
{
  "detail": "Superadmin privileges required"
}
```

---

## Admin creando usuario en su empresa

Un administrador de Empresa 1 puede crear:

```text
Usuario → Empresa 1
```

Resultado:

```text
HTTP 201 Created
```

---

## Admin intentando crear usuario en otra empresa

Un administrador de Empresa 1 intentando crear un usuario para Empresa 2 recibe:

```text
HTTP 403 Forbidden
```

Respuesta:

```json
{
  "detail": "You cannot create users in another company"
}
```

---

# 🧭 Frontend actual

El dashboard adapta las opciones visibles según el rol.

## Superadmin

Actualmente visualiza:

```text
Empresas
Usuarios
RBAC
Auditoría
```

## Admin

Actualmente visualiza:

```text
Usuarios
RBAC
Auditoría
```

## User

Actualmente visualiza:

```text
Mis permisos
```

### Importante

La interfaz solamente representa las opciones disponibles.

La seguridad real debe permanecer en los microservicios backend.

---

# 📁 Estructura del proyecto

La estructura principal es:

```text
devsecops-rbac-platform/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── servicios/
│   │
│   ├── api-gateway/
│   │   └── app/
│   │
│   ├── identity-service/
│   │   └── app/
│   │
│   ├── rbac-service/
│   │   └── app/
│   │
│   ├── audit-service/
│   │   └── app/
│   │
│   ├── sync-service/
│   │   └── app/
│   │
│   └── excel-worker/
│
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

---

# 🌿 Estrategia Git

La rama principal utilizada actualmente es:

```text
main
```

Los cambios importantes deben registrarse mediante commits descriptivos.

Ejemplos:

```bash
git add .
git commit -m "feat: add RBAC permissions management"
git push origin main
```

Convención recomendada:

```text
feat:     nueva funcionalidad
fix:      corrección
refactor: reorganización de código
test:     pruebas
docs:     documentación
security: cambios relacionados con seguridad
ci:       cambios en CI/CD
build:    cambios de construcción
chore:    mantenimiento
```

---

# 🔐 Filosofía DevSecOps

El proyecto busca implementar el principio:

> **Aprender antes de automatizar.**

La automatización debe construirse después de comprender:

- El código.
- La arquitectura.
- Las dependencias.
- Los riesgos.
- Los controles de seguridad.
- El flujo de despliegue.

La seguridad no debe aparecer únicamente al final del desarrollo.

---

# 🛡️ Seguridad en el ciclo de desarrollo

El pipeline objetivo contempla controles como:

```text
Developer
   │
   ▼
Git
   │
   ▼
Pull Request
   │
   ├── Lint
   ├── Unit Tests
   ├── SAST
   ├── SCA
   ├── Secret Scanning
   ├── IaC Scanning
   ├── Container Scanning
   ├── DAST
   └── SBOM
   │
   ▼
Build
   │
   ▼
Container Image
   │
   ▼
Security Validation
   │
   ▼
Deploy
```

---

# 🔎 SAST

Static Application Security Testing.

Objetivo:

Detectar vulnerabilidades directamente en el código fuente sin necesidad de ejecutar la aplicación.

Herramientas que pueden integrarse:

- SonarQube / SonarCloud.
- CodeQL.
- Semgrep.

---

# 📦 SCA

Software Composition Analysis.

Objetivo:

Analizar dependencias de terceros para detectar:

- Vulnerabilidades conocidas.
- Dependencias obsoletas.
- Riesgos en paquetes.
- Problemas de licenciamiento.

Herramientas consideradas durante el proyecto:

- Snyk.
- Dependabot.
- GitHub Advanced Security cuando esté disponible.

---

# 🔐 Secret Scanning

El pipeline debe evitar que se publiquen accidentalmente:

- Contraseñas.
- API Keys.
- Tokens.
- Claves privadas.
- Credenciales.
- Secretos JWT.
- Credenciales de bases de datos.

Los secretos deben manejarse mediante:

```text
.env
GitHub Secrets
Secret Managers
Variables de entorno
```

Nunca deben almacenarse directamente en el código fuente.

---

# 🐳 Seguridad de contenedores

Las imágenes Docker deben analizarse antes de ser utilizadas en ambientes superiores.

Controles previstos:

- Vulnerabilidades de paquetes.
- Vulnerabilidades de imágenes.
- Configuración insegura.
- Uso de imágenes base confiables.
- Reducción de privilegios.
- Ejecución como usuario no root cuando sea posible.

Herramientas posibles:

- Trivy.
- Snyk Container.
- Docker Scout.

---

# 🏗️ Seguridad de infraestructura

Si la infraestructura se automatiza mediante IaC, se deberán analizar los archivos antes del despliegue.

Herramientas posibles:

- Checkov.
- Snyk IaC.
- Terraform security scanners.

---

# 🌐 DAST

Dynamic Application Security Testing.

Objetivo:

Analizar la aplicación mientras está ejecutándose.

Herramienta principal considerada:

```text
OWASP ZAP
```

Puede utilizarse contra:

```text
http://localhost:8000
```

o posteriormente contra el ambiente desplegado.

---

# 📦 SBOM

Software Bill of Materials.

El proyecto puede generar un inventario de componentes utilizados por las aplicaciones y contenedores.

Objetivo:

Conocer:

```text
Aplicación
   │
   ├── Dependencia A
   ├── Dependencia B
   ├── Dependencia C
   └── Dependencia D
```

Esto facilita:

- Gestión de vulnerabilidades.
- Trazabilidad.
- Gestión de dependencias.
- Respuesta ante vulnerabilidades críticas.

---

# 🧪 Testing

La estrategia de pruebas contempla:

## Unit Tests

Pruebas de componentes individuales.

## Integration Tests

Pruebas entre:

```text
API
Database
Services
```

## API Tests

Validación de:

- HTTP status.
- Payload.
- Autenticación.
- Autorización.
- Validaciones.

## Security Tests

Pruebas destinadas a comprobar:

- Acceso no autorizado.
- Escalamiento de privilegios.
- Aislamiento entre empresas.
- Manipulación de tokens.
- Acceso a recursos de otras empresas.

---

# 🔥 Pruebas de aislamiento multiempresa

Estas pruebas son especialmente importantes.

Ejemplo:

```text
Usuario Empresa 1
       │
       ├── Recurso Empresa 1 → permitido
       │
       └── Recurso Empresa 2 → rechazado
```

El resultado esperado es:

```text
HTTP 403 Forbidden
```

o:

```text
HTTP 404 Not Found
```

según la estrategia de ocultamiento de recursos utilizada.

Nunca se debe confiar únicamente en:

```text
if (company_id === currentCompany)
```

dentro del frontend.

La comprobación debe existir en backend.

---

# 📈 Observabilidad

La arquitectura está preparada para evolucionar hacia una estrategia de observabilidad que incluya:

- Logs.
- Métricas.
- Trazas.
- Auditoría.
- Alertas.

Una evolución posible:

```text
Microservices
     │
     ├── Logs
     ├── Metrics
     └── Traces
             │
             ▼
       Observability
```

Herramientas que pueden evaluarse:

- Prometheus.
- Grafana.
- Loki.
- OpenTelemetry.

---

# ☸️ Evolución hacia Kubernetes

La arquitectura está diseñada de forma que los servicios puedan evolucionar posteriormente hacia Kubernetes.

Una posible estructura futura:

```text
Kubernetes Cluster
│
├── Namespace: dev
│
├── Namespace: staging
│
└── Namespace: production
     │
     ├── API Gateway
     ├── Identity Service
     ├── RBAC Service
     ├── Audit Service
     ├── Sync Service
     └── Workers
```

Los componentes de infraestructura podrían administrarse mediante:

- Deployments.
- Services.
- ConfigMaps.
- Secrets.
- Ingress.
- Persistent Volumes.
- Network Policies.

---

# ☁️ Evolución Cloud

La arquitectura puede adaptarse posteriormente a proveedores cloud como:

- AWS.
- Azure.
- Google Cloud.

La selección del proveedor dependerá de los objetivos académicos y técnicos del proyecto.

---

# 🗺️ Roadmap

## Fase 1 — Arquitectura base

- [x] Crear repositorio.
- [x] Crear arquitectura inicial de microservicios.
- [x] Crear Docker Compose.
- [x] API Gateway.
- [x] Identity Service.
- [x] RBAC Service.
- [x] Audit Service.
- [x] Sync Service.
- [x] PostgreSQL por servicio.
- [x] RabbitMQ.
- [x] MinIO.

---

## Fase 2 — Autenticación

- [x] Login.
- [x] Hash de contraseñas.
- [x] JWT.
- [x] Access Token.
- [x] Endpoint `/me`.
- [x] Expiración del token.
- [x] Usuario activo/inactivo.
- [x] Asociación usuario ↔ empresa.
- [x] Superadmin.
- [x] Admin.
- [x] User.

---

## Fase 3 — Autorización

- [x] Restricción de empresas.
- [x] Restricción de creación de usuarios.
- [x] Separación superadmin/admin.
- [x] Protección de administración de empresas.
- [x] Validación de empresa del administrador.

### Pendiente

- [ ] Autorización completa en RBAC Service.
- [ ] Autorización completa en Audit Service.
- [ ] Autorización completa en Sync Service.
- [ ] Validación de permisos específicos.
- [ ] Matriz RBAC completa.

---

# 🎨 Fase 4 — Frontend

- [x] React.
- [x] Vite.
- [x] Login.
- [x] Manejo de sesión.
- [x] Logout.
- [x] Consulta de `/me`.
- [x] Dashboard.
- [x] Dashboard según rol.
- [x] Diseño responsive.
- [x] Integración con API Gateway.

### Pendiente

- [ ] Módulo Empresas.
- [ ] Módulo Usuarios.
- [ ] Módulo RBAC.
- [ ] Módulo Auditoría.
- [ ] Módulo Excel.
- [ ] Gestión visual de permisos.
- [ ] Manejo avanzado de errores.
- [ ] Estados de carga.
- [ ] Validaciones de formularios.

---

# 📊 Fase 5 — RBAC completo

Pendiente:

```text
Empresa
   │
   ▼
Aplicación
   │
   ▼
Cargo
   │
   ▼
Rol
   │
   ▼
Permiso
```

Implementar:

- [ ] Roles.
- [ ] Relación rol-permiso.
- [ ] Relación cargo-rol.
- [ ] Relación usuario-cargo.
- [ ] Filtros por empresa.
- [ ] CRUD completo.
- [ ] Validación de autorización.
- [ ] Interfaz de matriz RBAC.

---

# 📑 Fase 6 — Excel

- [ ] Upload.
- [ ] Validación.
- [ ] Procesamiento.
- [ ] Sincronización.
- [ ] Exportación.
- [ ] Historial.
- [ ] Manejo de errores.
- [ ] Procesamiento asíncrono.
- [ ] Integración RabbitMQ.
- [ ] Almacenamiento MinIO.

---

# 📝 Fase 7 — Auditoría

- [ ] Registrar login.
- [ ] Registrar operaciones administrativas.
- [ ] Registrar modificaciones RBAC.
- [ ] Registrar importaciones.
- [ ] Registrar exportaciones.
- [ ] Consultar auditoría.
- [ ] Filtrar por usuario.
- [ ] Filtrar por empresa.
- [ ] Filtrar por fecha.
- [ ] Filtrar por servicio.

---

# 🔄 Fase 8 — CI/CD

Implementar pipeline automatizado:

```text
Push
 │
 ▼
Lint
 │
 ▼
Tests
 │
 ▼
SAST
 │
 ▼
SCA
 │
 ▼
Secret Scan
 │
 ▼
IaC Scan
 │
 ▼
Docker Build
 │
 ▼
Container Scan
 │
 ▼
DAST
 │
 ▼
SBOM
 │
 ▼
Artifact
 │
 ▼
Deploy
```

---

# 🛡️ Fase 9 — Seguridad avanzada

Pendiente:

- [ ] Rate limiting.
- [ ] Protección contra brute force.
- [ ] Rotación de secretos.
- [ ] Refresh tokens si el diseño final los requiere.
- [ ] Políticas de contraseña.
- [ ] Auditoría de eventos de seguridad.
- [ ] Seguridad de headers.
- [ ] Validación de inputs.
- [ ] Gestión centralizada de secretos.
- [ ] Network policies.
- [ ] Container hardening.

---

# 📚 Relación con DevSecOps

Este proyecto permite demostrar diferentes capacidades:

| Área | Implementación |
|---|---|
| Development | React + FastAPI |
| APIs | API Gateway + REST |
| Databases | PostgreSQL |
| Authentication | JWT |
| Authorization | RBAC |
| Containers | Docker |
| Orchestration | Docker Compose |
| Messaging | RabbitMQ |
| Object Storage | MinIO |
| Testing | Pytest / API tests |
| SAST | Sonar / CodeQL / Semgrep |
| SCA | Snyk / Dependabot |
| IaC Security | Checkov / Snyk |
| Container Security | Trivy / Snyk |
| DAST | OWASP ZAP |
| SBOM | Herramientas SBOM |
| CI/CD | GitHub Actions |
| Audit | Audit Service |
| Observability | Evolución futura |

---

# 🧠 Principios de diseño

## 1. Backend como fuente de verdad

Las decisiones de seguridad no deben depender del frontend.

---

## 2. Mínimo privilegio

Cada usuario debe tener únicamente los permisos necesarios para realizar sus funciones.

---

## 3. Separación de responsabilidades

Cada microservicio debe encargarse de un dominio específico.

---

## 4. Aislamiento por empresa

Los datos de una empresa no deben quedar accesibles para usuarios de otra empresa.

---

## 5. Seguridad desde el diseño

La seguridad se incorpora desde:

```text
Diseño
   ↓
Código
   ↓
Build
   ↓
Test
   ↓
Deploy
   ↓
Operación
```

---

## 6. Trazabilidad

Las operaciones importantes deben poder ser auditadas.

---

## 7. Automatización controlada

La automatización debe estar respaldada por comprensión técnica del proceso.

---

# ⚠️ Consideraciones de seguridad

Este proyecto se encuentra orientado principalmente a desarrollo, aprendizaje y demostración técnica.

Antes de utilizarlo en producción se deben revisar, entre otros:

- Gestión de secretos.
- HTTPS.
- Configuración CORS.
- Gestión de tokens.
- Rate limiting.
- Políticas de contraseña.
- Rotación de claves.
- Hardening de contenedores.
- Seguridad de PostgreSQL.
- Seguridad de RabbitMQ.
- Seguridad de MinIO.
- Logs.
- Monitoreo.
- Backups.
- Alta disponibilidad.
- Gestión de certificados.
- Gestión de vulnerabilidades.
- Configuración de infraestructura.

---

# 🚨 No subir secretos al repositorio

Nunca deben incluirse en Git:

```text
.env
Passwords
Private Keys
JWT Secrets
API Keys
Database credentials
Cloud credentials
SSH private keys
Tokens
```

Utilizar:

```text
.env
.env.example
GitHub Secrets
Secret Managers
```

El archivo `.env.example` debe contener únicamente ejemplos sin secretos reales.

Ejemplo:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
JWT_SECRET=CHANGE_ME
RABBITMQ_URL=amqp://USER:PASSWORD@HOST:5672/
MINIO_ACCESS_KEY=CHANGE_ME
MINIO_SECRET_KEY=CHANGE_ME
```

---

# 🧪 Estado actual del proyecto

Actualmente el proyecto cuenta con:

```text
✅ Arquitectura de microservicios
✅ Docker Compose
✅ API Gateway
✅ Identity Service
✅ RBAC Service
✅ Audit Service
✅ Sync Service
✅ PostgreSQL independiente por servicio
✅ RabbitMQ
✅ MinIO
✅ Autenticación JWT
✅ Login único
✅ Identificación automática de empresa
✅ Roles superadmin/admin/user
✅ Restricciones backend por empresa
✅ Frontend React
✅ Dashboard
✅ Dashboard según rol
✅ CORS configurado
✅ Pruebas de autenticación
✅ Pruebas de autorización
✅ Repositorio GitHub
```

El proyecto todavía se encuentra en construcción y las siguientes etapas están enfocadas principalmente en convertir los módulos existentes en funcionalidades completas de negocio y posteriormente automatizar los controles DevSecOps.

---

# 📌 Estado de Git

Repositorio:

```text
devsecops-rbac-platform
```

Rama principal:

```text
main
```

Último commit asociado al frontend y dashboard:

```text
338e35e
```

Mensaje:

```text
feat: add frontend authentication and role dashboard
```

---

# 👨‍💻 Desarrollo

El proyecto se desarrolla utilizando una metodología incremental:

```text
Diseñar
   ↓
Implementar
   ↓
Probar
   ↓
Validar seguridad
   ↓
Documentar
   ↓
Versionar
   ↓
Automatizar
```

Cada funcionalidad importante debe ser validada antes de continuar con la siguiente.

---

# 📜 Licencia

Proyecto académico y de aprendizaje orientado a DevSecOps, seguridad de aplicaciones, arquitectura de microservicios y control de acceso.

La licencia definitiva deberá establecerse de acuerdo con los requisitos del proyecto y de sus autores.

---

# 👥 Equipo

Proyecto desarrollado como iniciativa académica colaborativa.

Áreas principales:

- Backend.
- Frontend.
- DevOps.
- DevSecOps.
- Seguridad.
- Bases de datos.
- QA.
- Arquitectura.

---

# 🚀 Visión final

La visión de **DevSecOps RBAC Platform** es evolucionar desde una plataforma funcional de gestión RBAC hacia una solución completa donde:

```text
                    ┌──────────────────┐
                    │     Developer    │
                    └────────┬─────────┘
                             │
                             ▼
                         GitHub
                             │
                             ▼
                    ┌──────────────────┐
                    │     CI / CD      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
            SAST            SCA        Secret Scan
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                       Docker Build
                             │
                             ▼
                     Container Scan
                             │
                             ▼
                           DAST
                             │
                             ▼
                           SBOM
                             │
                             ▼
                         Deploy
                             │
                             ▼
                  ┌─────────────────────┐
                  │ RBAC Platform       │
                  │                     │
                  │ Identity            │
                  │ RBAC                │
                  │ Audit               │
                  │ Excel               │
                  │ Storage             │
                  └─────────────────────┘
                             │
                             ▼
                      Observability
```

El objetivo final es demostrar que una aplicación empresarial puede diseñarse incorporando **seguridad, automatización, trazabilidad y control de acceso desde el inicio del ciclo de vida del software**, y no como una actividad aislada al final del desarrollo.

---

## ⭐ Principio del proyecto

> **Aprender antes de automatizar. Construir antes de desplegar. Proteger antes de escalar.**
