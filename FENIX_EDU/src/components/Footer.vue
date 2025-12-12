<template>
  <footer class="footer">
    <div class="footer__container">
      <div class="footer__single-line">
        <div class="footer__brand">
          <div class="footer-logo">
            <span class="logo-icon">🎓</span>
            <h3 class="logo-text">FENIX.EDU</h3>
          </div>
        </div>

        <div class="footer__contacts-single">
          <div class="contact-item-single">
            <span class="contact-icon">📧</span>
            <span class="contact-text">support@fenixedu.ru</span>
          </div>
          <div class="contact-item-single">
            <span class="contact-icon">📞</span>
            <span class="contact-text">+7 (XXX) XXX-XX-XX</span>
          </div>
          <div class="contact-item-single">
            <span class="contact-icon">📍</span>
            <span class="contact-text"
              >ДВФУ. Приморский край, г. Владивосток, о. Русский, п. Аякс,
              10.</span
            >
          </div>
        </div>

        <div class="footer__copyright">© 2025 FENIX.EDU</div>
      </div>
    </div>
  </footer>
</template>

<script setup></script>

<style scoped>
.footer {
  background: #2f4156;
  color: white;
  padding: 1rem 2rem;
  margin-top: auto;
  position: relative;
  z-index: 10;
}

.footer__container {
  max-width: 1400px;
  margin: 0 auto;
}

.footer__single-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: nowrap;
}

.footer__brand {
  flex-shrink: 0;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin: 0;
  white-space: nowrap;
}

.footer__contacts-single {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex: 1;
  justify-content: center;
  flex-wrap: nowrap;
}

.contact-item-single {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
  padding: 0.25rem 0;
  white-space: nowrap;
}

.contact-item-single:hover {
  transform: translateY(-2px);
}

.contact-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.contact-text {
  color: #c8dae8;
  font-size: 0.9rem;
  white-space: nowrap;
}

.footer__copyright {
  color: #c8dae8;
  font-size: 0.85rem;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Адаптивность */
@media (max-width: 1100px) {
  .footer__single-line {
    gap: 1.5rem;
  }

  .footer__contacts-single {
    gap: 1.5rem;
  }
}

@media (max-width: 900px) {
  .footer__single-line {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }

  .footer__brand {
    order: 1;
    width: 100%;
    text-align: center;
    justify-content: center;
    margin-bottom: 0.5rem;
  }

  .footer__contacts-single {
    order: 3;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem 2rem;
  }

  .footer__copyright {
    order: 2;
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 1rem;
  }

  .footer__contacts-single {
    gap: 1rem;
  }

  .contact-text {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .footer__single-line {
    flex-direction: column;
    gap: 0.75rem;
  }

  .footer__brand {
    order: 1;
    width: auto;
    margin-bottom: 0;
  }

  .footer__copyright {
    order: 2;
  }

  .footer__contacts-single {
    order: 3;
    flex-direction: column;
    gap: 0.5rem;
    width: auto;
  }

  .contact-item-single {
    justify-content: center;
    width: 100%;
  }
}
</style>
