# Análise Completa do Workflow Multi-Agente: Estados, Fluxos e Conexões


```python
class PageChanges(BaseModel):
    """Estado completo de mudança em elemento HTML - auto-contido para aplicação"""
    change_id: str
    change_description: str
    original_state: HTMLElementState  # Estado completo antes da mudança
    target_state: HTMLElementState    # Estado completo desejado
    timestamp: str
    applied_timestamp: Optional[str]
    version: str  # Versionamento semântico (x.y.z) para rollback
    applied: bool = False
    
    # NOVA CONEXÃO COM WORKFLOW
    step_id: str = Field(description="ID do CustomizationStep que gerou esta mudança")
    step_description: str = Field(description="Descrição do step para contexto")
    execution_order: int = Field(description="Ordem de execução dentro do step")
    
    # CONTEXTO ADICIONAL PARA TRACKING
    application_status: Literal["pending", "applied", "failed", "rolled_back"] = "pending"
    error_message: Optional[str] = Field(description="Erro se aplicação falhou")

class HTMLElementState(BaseModel):
    """Estado completo auto-contido de um elemento HTML"""
    element_id: str
    element_tag: str
    css_selector: str
    text_content: Optional[str]
    inner_html: Optional[str]
    attributes: HTMLAttributes
    inline_styles: CSSDeclaration
    is_visible: bool = True
    is_interactive: bool = True
    parent_selector: Optional[str]
    children_selectors: List[str]
    modification_timestamp: str
    modification_reason: str
```

## Arquitetura Completa: Storytelling dos Modelos

### **Camada 1: Dados Fundamentais (Foundation Layer)**

**Propósito:** Representar informações básicas do domínio

```mermaid
---
config:
  layout: dagre
---
classDiagram
direction LR
    class UserData {
        user_id
        first_name
        last_name
        email
        role
    }
    class BankData {
        bank_name
        website
        primary_color
        secondary_color
    }
    class BrandingData {
        colors
        logos
        primary_font
        secondary_font
    }

    UserData -- BankData : configures
    BankData -- BrandingData : generates
```

**História:** Um usuário (`UserData`) configura dados do banco (`BankData`) que são usados para extrair informações de branding (`BrandingData`) do website institucional.

### **Camada 2: Estruturas HTML (Content Layer)**

**Propósito:** Representar elementos de página que podem ser modificados

```mermaid
classDiagram
    direction LR
    class HTMLElement {
        +String element_id
        +String element_tag
        +String text_content
        +HTMLAttributes attributes
        +boolean customizable
    }
    
    class HTMLAttributes {
        +String style
        +String css_class
        +String data_role
        +String aria_label
        +boolean aria_hidden
        +int tabindex
    }
    
    class Question {
        +String question_id
        +String question_text
        +String question_type
        +boolean required
        +String choices
        +String answer
    }
    
    HTMLElement "1" -- "1" HTMLAttributes : has
    HTMLElement "1" -- "*" Question : configures

```

**História:** Elementos HTML (`HTMLElement`) possuem atributos estruturados (`HTMLAttributes`) e podem ser configurados através de perguntas (`Question`) feitas ao usuário.

### **Camada 3: Mudanças e Transformações (Change Layer)**

**Propósito:** Representar transformações aplicadas aos elementos

```mermaid
classDiagram
    direction LR
    
    class HTMLElementState {
        +str element_id
        +str element_tag
        +str css_selector
        +Optional[str] text_content
        +Optional[str] inner_html
        +HTMLAttributes attributes
        +CSSDeclaration inline_styles
        +bool is_visible
        +bool is_interactive
        +str modification_timestamp
        +str modification_reason
    }
    
         class PageChanges {
         +str change_id
         +str change_description
         +HTMLElementState original_state
         +HTMLElementState target_state
         +str timestamp
         +Optional[str] applied_timestamp
         +str version
         +bool applied
         +str step_id
         +str step_description
         +int execution_order
     }
    
    class HTMLAttributes {
        +Optional[str] id
        +List[str] class_list
        +List[DataAttribute] data_attributes
        +Optional[bool] disabled
        +Optional[bool] hidden
    }
    
    class CSSDeclaration {
        +List[CSSProperty] properties
        +add_property()
        +to_css_string()
    }
    
    PageChanges "1" *-- "2" HTMLElementState : original/target
    HTMLElementState "1" *-- "1" HTMLAttributes : contains
    HTMLElementState "1" *-- "1" CSSDeclaration : contains

```

**História:** Estados completos de elementos HTML (`HTMLElementState`) representam tanto o estado original quanto o estado desejado, encapsulados em `PageChanges` que conecta as transformações com contexto completo de workflow. Cada estado é auto-contido com todos os dados necessários para aplicação direta.

### **Camada 4: Workflow e Steps (Process Layer)**

**Propósito:** Orquestrar a execução de mudanças através de steps estruturados

```mermaid
classDiagram
    direction LR
    class CustomizationStep {
        +str step_id
        +str description
        +str[] tools_required
        +str expected_outcome
        +bool completed
    }
    
    class PageModel {
        +str page_id
        +str name
        +str microapp
        +str version
        +str html_raw
        +HTMLElement[] html_elements
        +str updated_at
        +str introduction
        +Question[] predefined_questions
        +PageChanges[] changes
    }
    
    class SystemCapability {
        +str capability_name
        +str description
        +str[] required_tools
        +str entry_agent
    }
    
    class PageChanges {
        +str change_id
        +str change_type
        +str change_description
    }
    
    class HTMLElement {
        // Attributes for HTMLElement can be defined here if needed
    }
    
    class Question {
        // Attributes for Question can be defined here if needed
    }
    
    PageModel "1" o-- "0..*" HTMLElement : contains
    PageModel "1" o-- "0..*" Question : defines
    PageModel "1" o-- "0..*" PageChanges : tracks
    SystemCapability "1" -- "0..*" CustomizationStep : enables

```

**História:** Steps de customização (`CustomizationStep`) geram mudanças (`PageChanges`) que são aplicadas a páginas (`PageModel`) usando capacidades do sistema (`SystemCapability`).

### **Camada 5: Estados de Workflow (State Layer)**

**Propósito:** Gerenciar estado e progressão através dos workflows

```mermaid
classDiagram
    direction LR

    class PrototypeStateSchema {
        +user_data: UserData
        +bank_data: BankData
        +branding_data: BrandingData
        +available_pages: PageModel[]
        +selected_page: PageModel
        +status: WorkflowStatus
        +metadata: ProcessingMetadata
        +steps: CustomizationStep[]
        +messages: String[]
    }

    class PageCustomizationState {
        +steps: CustomizationStep[]
        +messages: Message[]
        +selected_page: PageModel
        +current_step_index: int
        +processing_started: bool
        +change_plan: PageChanges[]
        +applied_changes: PageChanges[]
        +final_thoughts: String
    }

    class BrandingExtractionState {
        +website_url: String
        +extraction_started: bool
        +extracted_colors: String[]
        +extracted_logos: String[]
        +extracted_branding: BrandingData
        +extraction_successful: bool
        +extraction_errors: String[]
    }

    class UserData
    class BankData
    class BrandingData
    class PageModel
    class CustomizationStep
    class WorkflowStatus
    class ProcessingMetadata
    class Message
    class PageChanges

    %% Composições e Agregações

    PrototypeStateSchema *-- UserData
    PrototypeStateSchema *-- BankData
    PrototypeStateSchema *-- BrandingData
    PrototypeStateSchema *-- PageModel : contains
    PrototypeStateSchema *-- CustomizationStep : includes
    PrototypeStateSchema o-- PageCustomizationState
    PrototypeStateSchema o-- BrandingExtractionState

    PageCustomizationState *-- PageModel
    PageCustomizationState *-- CustomizationStep
    PageCustomizationState *-- PageChanges
    PageCustomizationState *-- Message

    BrandingExtractionState *-- BrandingData

```

**História:** Estados principais (`PrototypeStateSchema`) orquestram sub-workflows (`PageCustomizationState`, `BrandingExtractionState`) que executam operações específicas e mantêm tracking detalhado de progresso.

## Fluxo de Execução Completo

### **Sequência 1: Inicialização e Setup**

```mermaid
sequenceDiagram
    participant U as User
    participant PS as PrototypeStateSchema
    participant BES as BrandingExtractionState
    participant BD as BrandingData
    
    Note over U,BD: Fase 1: Setup e Extração de Branding
    
    U->>PS: Fornece UserData + BankData
    PS->>PS: status = "initializing"
    PS->>BES: website_url = bank_data.website
    BES->>BES: extraction_started = True
    
    BES->>BD: Extract colors, logos, fonts
    BD-->>BES: extracted_branding
    BES->>BES: extraction_successful = True
    
    BES->>PS: Update branding_data
    PS->>PS: status = "branding_extracted"
```

### **Sequência 2: Seleção de Página e Planning**

```mermaid
sequenceDiagram
    participant PS as PrototypeStateSchema
    participant PM as PageModel
    participant Q as Question
    participant CS as CustomizationStep
    
    Note over PS,CS: Fase 2: Seleção e Planning
    
    PS->>PM: Load available_pages
    PM->>PS: Lista de páginas disponíveis
    
    U->>PS: Seleciona página específica
    PS->>PS: selected_page = chosen_page
    
    PS->>Q: Load predefined_questions
    Q->>U: Apresenta perguntas de configuração
    U->>Q: Fornece respostas
    
    PS->>CS: Generate customization steps
    CS->>PS: Lista de steps planejados
    PS->>PS: status = "planning_complete"
```

### **Sequência 3: Execução de Customização**

```mermaid
sequenceDiagram
    participant PS as PrototypeStateSchema
    participant PCS as PageCustomizationState
    participant CS as CustomizationStep
    participant PC as PageChanges
    participant HE as HTMLElement
    
    Note over PS,HE: Fase 3: Execução de Mudanças
    
    PS->>PCS: Convert state + transfer steps
    PCS->>PCS: processing_started = True
    
    loop For each CustomizationStep
        PCS->>CS: Execute step[current_step_index]
        CS->>PC: Generate PageChanges with step_id
        PC->>PC: step_description = CS.description
        PC->>PC: application_status = "pending"
        
        PCS->>PC: Add to change_plan
        
        PCS->>HE: Apply change_data to element_id
        HE-->>PCS: Application result
        
        alt Success
            PC->>PC: applied = True, status = "applied"
            PCS->>PC: Move to applied_changes
            CS->>CS: completed = True
        else Failure
            PC->>PC: status = "failed", error_message
            PCS->>PCS: Handle error / retry
        end
        
        PCS->>PCS: current_step_index += 1
    end
    
    PCS->>PS: Return updated state with results
    PS->>PS: status = "customization_complete"
```

### **Sequência 4: Tracking e Auditoria**

```mermaid
sequenceDiagram
    participant PM as PageModel
    participant PC as PageChanges
    participant CS as CustomizationStep
    participant Audit as AuditSystem
    
    Note over PM,Audit: Fase 4: Tracking e Auditoria
    
    PM->>PC: Access changes history
    PC->>PC: Group by step_id
    PC->>CS: Link to CustomizationStep details
    
    loop For each change group
        PC->>Audit: Report execution_order
        PC->>Audit: Report application_status
        PC->>Audit: Report step_description
        CS->>Audit: Report tools_required
        CS->>Audit: Report expected_outcome
    end
    
    Audit->>PM: Generate complete audit trail
    PM->>U: Present change summary with context
```

## Storytelling Completo: A Jornada do Workflow

### **Ato I: O Usuário e Sua Necessidade**
A história começa quando um usuário (`UserData`) acessa o sistema com a necessidade de customizar uma página bancária. Ele fornece dados básicos do banco (`BankData`) incluindo o website institucional. O sistema então inicia um sub-workflow de extração (`BrandingExtractionState`) que analisa o website e extrai cores, logos e fontes, criando um perfil de branding (`BrandingData`) completo.

### **Ato II: Descoberta e Planejamento**
Com o branding extraído, o sistema apresenta páginas disponíveis (`PageModel`) que contêm elementos customizáveis (`HTMLElement`) com atributos estruturados (`HTMLAttributes`). O usuário responde perguntas predefinidas (`Question`) que orientam o processo de customização. Baseado nessas respostas e no branding extraído, o sistema gera uma série de steps de customização (`CustomizationStep`) que descrevem exatamente o que será modificado.

### **Ato III: Execução e Transformação**
O workflow entra na fase de execução (`PageCustomizationState`) onde cada step é processado sequencialmente. Para cada step, o sistema gera mudanças específicas (`PageChanges`) que capturam o **estado completo** do elemento antes (`original_state`) e depois (`target_state`) das modificações. Cada `HTMLElementState` é auto-contido com todos os atributos, estilos e dados necessários para aplicação direta. **Crucialmente**, cada mudança está conectada ao step que a gerou através de `step_id`, `step_description` e `execution_order`, criando rastreabilidade completa.

### **Ato IV: Aplicação e Validação**
As mudanças são aplicadas aos elementos HTML com tracking detalhado de status (`application_status`). Se uma aplicação falha, o erro é capturado (`error_message`) e o rollback é feito através do histórico versionado de mudanças. O sistema mantém listas separadas de mudanças planejadas (`change_plan`) e aplicadas (`applied_changes`), permitindo comparação e auditoria baseada em versões semânticas.

### **Ato V: Auditoria e Conclusão**
Ao final, o sistema possui uma trilha completa de auditoria onde cada mudança pode ser rastreada até o step específico que a originou, com contexto completo sobre tools utilizadas, outcomes esperados, e status de execução. Isso permite debugging eficiente, rollbacks seletivos, e relatórios detalhados para o usuário.
