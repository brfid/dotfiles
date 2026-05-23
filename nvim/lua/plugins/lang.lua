return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        -- JSON: outline symbols + validation
        jsonls = {},
        -- YAML: outline symbols + validation
        yamlls = {
          settings = {
            yaml = {
              schemaStore = { enable = true, url = "https://www.schemastore.org/api/json/catalog.json" },
            },
          },
        },
      },
    },
  },
}
