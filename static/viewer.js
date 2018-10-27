let showOpcodes = true;

function toggleOpcodes(e) {
  showOpcodes = !showOpcodes;

  document.querySelectorAll('.opcodes').forEach(opcode => {
    if (showOpcodes) opcode.classList.remove('hidden');
    else opcode.classList.add('hidden');
  });

  if (e) e.preventDefault();
}

toggleOpcodes();
