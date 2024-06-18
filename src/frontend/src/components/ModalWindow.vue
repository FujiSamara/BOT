<template>
  <div class="wrapper">
    <div class="window">
      <window-cross class="cross"></window-cross>
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
  background-color: rgba(0, 0, 0, 0.5);
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.window {
  background-color: white;
  border-radius: 29px;
  width: 500px;
  height: 300px;
}

.cross {
  margin-left: auto;
  margin-right: 10px;
  margin-top: 10px;
}
</style>
