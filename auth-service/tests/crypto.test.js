process.env.SESSION_ENCRYPTION_KEY = 'test_key_32_chars_for_unit_tests!';

const { encrypt, decrypt } = require('../src/utils/crypto');

describe('Crypto - AES-256-GCM', () => {
  const payload = { userId: 'uuid-1', username: 'juanperez', phone: '3001234567' };

  it('cifra y descifra correctamente', () => {
    const encrypted = encrypt(payload);
    const decrypted = decrypt(encrypted);
    expect(decrypted).toEqual(payload);
  });

  it('produce texto cifrado diferente cada vez (IV aleatorio)', () => {
    const a = encrypt(payload);
    const b = encrypt(payload);
    expect(a).not.toBe(b);
  });

  it('falla al descifrar datos corruptos', () => {
    expect(() => decrypt('invalido:datos:corruptos')).toThrow();
  });
});
