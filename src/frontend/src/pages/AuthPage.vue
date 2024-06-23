<template>
    <div class="content">
        <modal-window class="modal-window">
            <div class="label">
                <div class="keys"></div>
                <p>Авторизуйтесь</p>
            </div>
            <form>
                <border-input placeholder="Логин"></border-input>
                <border-input placeholder="Пароль"></border-input>  
            </form>
        </modal-window>
    </div>
</template>
<script setup lang="ts">
import ModalWindow from '@/components/ModalWindow.vue'
</script>
<style scoped>
.content {
    background-image: url('img/auth-bg.jpg');
    background-size: cover;
    width: 100%;
    height: 100%;
}

.label {
  width: 460px;
  height: 145px;
  display: flex;
  gap: 20px;
  flex-direction: column;
  align-items: center;
}

.label .keys {
  width: 96px;
  height: 96px;
  background-image: url('img/auth-keys.gif');
  background-size: cover;
}

@font-face {
  font-family: benzin-regular;
  src: url('font/benzin-regular.ttf') format('truetype');
}

.label p {
  font-weight: 600;
  font-size: 28px;
  font-family: benzin-regular;
  margin: 0;
  color: #292929;
}

form {
  width: 100%;
  height: 90px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>