return {
  "hedyhli/outline.nvim",
  lazy = true,
  cmd = { "Outline", "OutlineOpen" },
  keys = {
    { "<leader>o", "<cmd>Outline<CR>", desc = "Toggle outline" },
  },
  init = function()
    vim.api.nvim_create_autocmd("LspAttach", {
      once = true,
      callback = function()
        require("outline").open({ focus_outline = false })
      end,
    })
  end,
  opts = {
    outfold_depth = false,
  },
}
