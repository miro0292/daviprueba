package com.financial.orchestrator.util;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HexFormat;

/**
 * Descifra sesiones cifradas con AES-256-GCM por el auth-service (Node.js).
 * Formato almacenado en Redis: ivHex:authTagHex:encryptedHex
 */
@Component
public class CryptoUtil {

    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final int GCM_TAG_BITS = 128;

    private final SecretKeySpec secretKey;

    public CryptoUtil(@Value("${app.session.encryption-key}") String encryptionKey) {
        byte[] keyBytes = Arrays.copyOf(encryptionKey.getBytes(StandardCharsets.UTF_8), 32);
        this.secretKey = new SecretKeySpec(keyBytes, "AES");
    }

    public String decrypt(String ciphertext) {
        try {
            String[] parts = ciphertext.split(":");
            if (parts.length != 3) throw new IllegalArgumentException("Formato de sesión inválido");

            HexFormat hex = HexFormat.of();
            byte[] iv = hex.parseHex(parts[0]);
            byte[] authTag = hex.parseHex(parts[1]);
            byte[] encrypted = hex.parseHex(parts[2]);

            // Java GCM espera: ciphertext || authTag concatenados
            byte[] ciphertextWithTag = new byte[encrypted.length + authTag.length];
            System.arraycopy(encrypted, 0, ciphertextWithTag, 0, encrypted.length);
            System.arraycopy(authTag, 0, ciphertextWithTag, encrypted.length, authTag.length);

            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, secretKey, new GCMParameterSpec(GCM_TAG_BITS, iv));

            byte[] decrypted = cipher.doFinal(ciphertextWithTag);
            return new String(decrypted, StandardCharsets.UTF_8);
        } catch (Exception e) {
            throw new RuntimeException("Error al descifrar sesión", e);
        }
    }
}
