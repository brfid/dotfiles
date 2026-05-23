-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Insert mode: move by display line (respects soft-wrapped lines)
vim.keymap.set("i", "<Up>", "<C-o>gk", { noremap = true, silent = true })
vim.keymap.set("i", "<Down>", "<C-o>gj", { noremap = true, silent = true })
vim.keymap.set("i", "<Home>", "<C-o>g0", { noremap = true, silent = true })
vim.keymap.set("i", "<End>", "<C-o>g$", { noremap = true, silent = true })
