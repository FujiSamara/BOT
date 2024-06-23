<template>
  <div class="wrapper">
    <div class="window">
      <window-cross class="cross"></window-cross>
      <div class="label">
        <div class="keys"></div>
        <p>Авторизуйтесь</p>
      </div>
      <div></div>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
<script>
export default {
  name: "modal-window",
};
</script>
<style scoped>
.wrapper {
  background-color: rgba(0, 0, 0, 0.3);
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.window {
  background-color: white;
  border-radius: 40px;
  width: 560px;
  height: 480px;
  padding: 50px;
  gap: 40px;
  position: relative;
  flex-direction: column;
  display: flex;
}

.cross {
  position: absolute;  
  top: 27px;
  right: 27px;
}

.label {
  width: 460px;
  height: 140px;
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
</style>
