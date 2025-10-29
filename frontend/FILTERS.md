# Frontend - Filtros NLP

## ✨ Novas Funcionalidades

O frontend agora permite que o usuário escolha dinamicamente quais filtros aplicar durante a busca:

### 🎛️ Controles de Filtro

1. **Remover Plurais**
   - ✅ Ativado: Remove palavras no plural (casas, livros, etc.)
   - ❌ Desativado: Mantém todas as palavras

2. **Remover Verbos Conjugados**
   - ✅ Ativado: Remove verbos conjugados (amava, comendo, etc.)
   - ❌ Desativado: Mantém todos os verbos

### 📡 Integração com Backend

Os filtros são enviados como parâmetros da query string:

```
GET /api/search?allowed_letters=abc&required_letter=a&min_length=4&filter_plurals=true&filter_conjugated_verbs=true
```

### 🎨 Interface

**Novos Elementos:**
- Seção "Filtros NLP (SpaCy)" no formulário de busca
- Checkboxes estilizados com descrições
- Badges visuais nos resultados mostrando filtros ativos
- Mensagem atualizada quando não há resultados

**Estilos Adicionados:**
- `.filter-options` - Container dos filtros
- `.checkbox-group` - Grupo de checkboxes
- `.checkbox-label` - Label dos checkboxes com hover
- `.checkbox-text` - Texto explicativo
- `.filter-badge` - Badge destacado nos resultados

### 💡 Estado Padrão

Por padrão, ambos os filtros estão **habilitados** (true):
- `filterPlurals: true`
- `filterConjugatedVerbs: true`

O usuário pode desmarcar os checkboxes para desabilitar os filtros.

### 📊 Feedback Visual

Quando filtros estão ativos, badges aparecem nos resultados:
- 🚫 **Plurals** - Filtro de plurais ativo
- 🚫 **Conjugated** - Filtro de verbos ativo

### 🔄 Como Funciona

1. Usuário marca/desmarca os checkboxes
2. Ao clicar em "Search Words", os parâmetros são enviados
3. Backend aplica os filtros usando SpaCy
4. Resultados filtrados são exibidos
5. Badges mostram quais filtros foram aplicados

### 🧪 Testando

```bash
# Frontend
cd frontend
npm run dev

# Backend (em outro terminal)
cd backend
uv run python app.py

# Acessar: http://localhost:5173
```

### 📝 Exemplo de Uso

**Sem filtros:**
- Busca: letras "abc", letra obrigatória "a"
- Resultados: casa, casas, amar, amava, acabar, acabava, etc.

**Com filtro de plurais:**
- Resultados: casa, amar, amava, acabar, acabava, etc.
- Removidos: casas

**Com ambos os filtros:**
- Resultados: casa, amar, acabar, etc.
- Removidos: casas, amava, acabava

### 🎯 Benefícios

- ✅ Controle total do usuário
- ✅ Interface intuitiva
- ✅ Feedback visual claro
- ✅ Funciona dinamicamente sem recarregar página
- ✅ Performance otimizada (filtros aplicados sob demanda)

### 🔧 Modificações nos Arquivos

**Frontend:**
- `src/App.jsx` - Adiciona estados e lógica dos filtros
- `src/App.css` - Estilos para os novos elementos

**Backend:**
- `src/routes.py` - Aceita parâmetros de filtro e aplica dinamicamente

### 📖 Documentação Técnica

Ver:
- [INSTALL_UV.md](../backend/INSTALL_UV.md) - Como instalar e configurar
- [SPACY_IMPLEMENTATION.md](../backend/SPACY_IMPLEMENTATION.md) - Detalhes técnicos dos filtros
