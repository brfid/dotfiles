return {
  "hedyhli/outline.nvim",
  keys = { { "<leader>o", "<cmd>Outline<cr>", desc = "Toggle Outline" } },
  opts = {
    outline_window = {
      -- Don't steal focus on open, matching VSCode secondary-sidebar behaviour.
      -- Cursor stays in the editor; outline tracks it automatically.
      focus_on_open = false,
      width = 25,
      relative_width = false,
    },
  },
}
