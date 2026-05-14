package com.financial.orchestrator.util;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class CryptoUtilTest {

    // Misma clave que usa el auth-service en tests
    private final CryptoUtil cryptoUtil = new CryptoUtil("test_key_32_chars_for_unit_tests!");

    @Test
    void decrypt_invalidFormat_throwsException() {
        assertThatThrownBy(() -> cryptoUtil.decrypt("invalid_data"))
            .isInstanceOf(RuntimeException.class)
            .hasMessageContaining("descifrar");
    }

    @Test
    void decrypt_corruptedData_throwsException() {
        assertThatThrownBy(() -> cryptoUtil.decrypt("aabbcc:ddeeff:001122"))
            .isInstanceOf(RuntimeException.class);
    }

    @Test
    void decrypt_wrongNumberOfParts_throwsException() {
        assertThatThrownBy(() -> cryptoUtil.decrypt("onlyonepart"))
            .isInstanceOf(RuntimeException.class);
    }
}
