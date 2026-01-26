# Samsung AC Display Light (Home Assistant)

<div align="center">
  <img src="https://raw.githubusercontent.com/Otanar1/samsung-ac-lighting/main/custom_components/samsung_ac_lighting/logo.png" alt="Samsung AC Display Light" width="60%">
</div>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Otanar1/samsung-ac-lighting)](https://github.com/Otanar1/samsung-ac-lighting/releases)

---

### 🌍 Language / Idioma
[🇧🇷 Português (Brasil)](#português-brasil) | [🇺🇸 English](#english)

---

<a name="português-brasil"></a>
## 🇧🇷 Português (Brasil)

Integração personalizada para controlar o LED/display de aparelhos de ar-condicionado Samsung via **SmartThings Cloud API**.  
Diferente da integração oficial, esta foca em funcionalidades específicas que geralmente não estão expostas, como o controle da luz do display e o modo de limpeza automática.

### ✨ Funcionalidades

- **💡 Controle de LED:** Liga e desliga o display digital do ar-condicionado.
- **🧹 Auto Cleaning:** Controle do modo de Limpeza Automática (funcionalidade exclusiva).
- **⏱️ Auto LED Off:** Desliga o LED automaticamente após um tempo configurável (Timer).
- **🎛️ Controles na Dashboard:** Configuração feita através de entidades nativas (Switch e Select).
- **🚀 UI Otimista:** Feedback visual instantâneo nos botões (sem lag ao clicar).
- **🔄 Sincronização:** Reflete mudanças feitas pelo controle remoto físico.
- **Eficiência:** Utiliza `DataUpdateCoordinator` para evitar limites de requisição da API (Rate Limits).

### 🔑 Gerando o Token (Obrigatório)

Antes de instalar, você precisa gerar um **Token de Acesso Pessoal (PAT)** na Samsung. Isso permite que o Home Assistant controle seus dispositivos.

1. Acesse: [https://account.smartthings.com/tokens](https://account.smartthings.com/tokens)
2. Faça login com sua conta Samsung/SmartThings.
3. Clique em **Generate new token**.
4. Dê um nome para o token (Ex: `Home Assistant`).
5. Em **Authorized Scopes**, marque **todas as permissões** (ou certifique-se de marcar as opções de *Devices*).
6. Clique em **Generate token**.
7. **Copie e salve o código!** Ele não será mostrado novamente.

> ⚠️ **IMPORTANTE:** Este token concede acesso total aos seus dispositivos SmartThings. Guarde-o em local seguro e não compartilhe com ninguém.

### 📦 Instalação (via HACS)

1. No Home Assistant, vá em **HACS** > **Integrações**.
2. Clique nos 3 pontinhos no canto superior direito > **Repositórios Personalizados**.
3. Cole a URL deste repositório e selecione a categoria **Integration**.
4. Clique em **Instalar**.
5. **Reinicie o Home Assistant**.

### ⚙️ Configuração

#### 1. Conexão
1. Vá em **Configurações** > **Dispositivos e Serviços**.
2. Clique em **Adicionar integração**.
3. Procure por **Samsung AC Display Light**.
4. Cole o seu **Token do SmartThings**.
5. Selecione o dispositivo (ar-condicionado) que deseja controlar.

#### 2. Configuração do "Auto LED" (Timer)
Esta integração cria entidades de configuração diretamente na página do dispositivo. Você pode adicioná-las ao seu painel (Dashboard):

| Entidade | Tipo | Função |
| :--- | :--- | :--- |
| `switch.auto_led_off` | Switch | Ativa/Desativa o desligamento automático do LED. |
| `select.tempo_auto_off` | Select | Define o tempo de espera para apagar (5s, 15s, 30s, 60s, 120s). |

*Nota: As configurações são salvas automaticamente e restauradas mesmo após reiniciar o Home Assistant.*

### 🛠️ Melhorias Futuras
- Controles adicionais: Beep (Efeito sonoro), Quiet Mode e WindFree.

---

<a name="english"></a>
## 🇺🇸 English

Custom integration to control the LED/display of Samsung air conditioners via **SmartThings Cloud API**.  
Unlike the official integration, this one focuses on specific features that are often unexposed, such as display light control and auto-cleaning mode.

### ✨ Features

- **💡 LED Control:** Turn the air conditioner digital display on and off.
- **🧹 Auto Cleaning:** Control the Auto Cleaning mode (exclusive feature).
- **⏱️ Auto LED Off:** Automatically turns off the LED after a configurable time.
- **🎛️ Dashboard Controls:** Configuration handled via native entities (Switch and Select).
- **🚀 Optimistic UI:** Instant visual feedback on buttons (no lag when clicking).
- **🔄 State Sync:** Reflects changes made by the physical remote control.
- **Efficiency:** Uses `DataUpdateCoordinator` to respect API Rate Limits.

### 🔑 Generating the Token (Required)

Before installing, you need to generate a **Personal Access Token (PAT)** at Samsung. This authorizes Home Assistant to control your devices.

1. Go to: [https://account.smartthings.com/tokens](https://account.smartthings.com/tokens)
2. Log in with your Samsung/SmartThings account.
3. Click on **Generate new token**.
4. Name the token (e.g., `Home Assistant`).
5. Under **Authorized Scopes**, check **all permissions** (or ensure *Devices* options are checked).
6. Click on **Generate token**.
7. **Copy and save the code!** It will not be shown again.

> ⚠️ **IMPORTANT:** This token grants full access to your SmartThings devices. Keep it safe and do not share it.

### 📦 Installation (via HACS)

1. In Home Assistant, go to **HACS** > **Integrations**.
2. Click the 3 dots in the top right corner > **Custom Repositories**.
3. Paste this repository URL and select **Integration** as the category.
4. Click **Install**.
5. **Restart Home Assistant**.

### ⚙️ Configuration

#### 1. Setup
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Samsung AC Display Light**.
4. Paste your **SmartThings Token**.
5. Select the device (air conditioner) you want to control.

#### 2. "Auto LED" Configuration (Timer)
This integration creates configuration entities directly on the device page. You can add them to your Lovelace dashboard:

| Entity | Type | Function |
| :--- | :--- | :--- |
| `switch.auto_led_off` | Switch | Enables/Disables the auto-off feature for the LED. |
| `select.tempo_auto_off` | Select | Sets the delay time before turning off (5s, 15s, 30s, 60s, 120s). |

*Note: Settings are automatically saved and restored even after Home Assistant restarts.*

### 🛠️ Planned Improvements
- Additional controls: Beep (Sound Effect), Quiet Mode, and WindFree.

---

## 📄 License

MIT