# Samsung AC Display Light (Home Assistant)

<div align="center">
  <img src="logo.png" alt="Logo" width="100%">
</div>

Integração personalizada para controlar o LED/display de aparelhos de ar-condicionado Samsung via **SmartThings Cloud API**.

Custom integration to control the LED/display of Samsung air conditioners via **SmartThings Cloud API**.

---

## ✨ Funcionalidades | Features

- 💡 **Controle de LED:** Liga/desliga o display do ar-condicionado.
- 🧹 **Auto Cleaning:** Controle de Limpeza Automática (funcionalidade exclusiva).
- ⏱️ **Auto LED Off:** Desliga o LED automaticamente após um tempo configurável.
- 🎛️ **Controles na Dashboard:** Configuração feita através de entidades nativas (Switch e Select).
- 🚀 **UI Otimista:** Feedback visual instantâneo (sem lag ao clicar).
- 🔄 **Sincronização:** Reflete mudanças feitas pelo controle remoto.
- **Eficiência:** Usa `DataUpdateCoordinator` para evitar limites da API (Rate Limits).

---

## 📦 Instalação (HACS) | Installation (HACS)

1. Adicione este repositório como **Custom Repository** no HACS.
2. Tipo: **Integration**.
3. Instale a integração.
4. Reinicie o Home Assistant.

---

## ⚙️ Configuração | Configuration

### 1. Conexão (Setup)
1. Vá em **Configurações → Dispositivos e Serviços**.
2. Clique em **Adicionar integração**.
3. Procure por **Samsung AC Display Light**.
4. Informe:
   - **SmartThings Personal Access Token**.
   - Selecione o **ar-condicionado desejado**.

### 2. Configuração do Auto LED (Dashboard)
Esta integração cria entidades de configuração diretamente na página do dispositivo. Você pode adicioná-las ao seu painel Lovelace:

| Entidade | Tipo | Função |
| :--- | :--- | :--- |
| `switch.auto_led_off` | Switch | Ativa/Desativa o desligamento automático do LED. |
| `select.tempo_auto_off` | Select | Define o tempo de espera (5s, 15s, 30s, 60s, 120s). |

*Nota: As configurações são salvas e restauradas automaticamente mesmo após reiniciar o Home Assistant.*

---

## 🔁 Sincronização de Estado | State Sync

- Alterações feitas pelo **controle remoto** são refletidas automaticamente no Home Assistant.
- O estado dos botões no Home Assistant sempre tenta prever a ação (UI Otimista) e depois confirma com a nuvem.

---

## 🧠 Arquitetura | Architecture

- SmartThings Cloud API
- DataUpdateCoordinator (Polling de 15s)
- Dashboard Entities (Switch/Select) para configuração
- RestoreEntity para persistência de dados

---

## 🛠️ Próximas melhorias | Planned Improvements

- Expor controles adicionais:
  - Beep (Sound Effect)
  - Quiet Mode
  - WindFree

---

## ⚠️ Observações | Notes

- Requer conexão constante com a internet (Cloud API).
- Pode haver limites de requisição impostos pela SmartThings API se usar muitos dispositivos.

---

## 📄 Licença | License

MIT