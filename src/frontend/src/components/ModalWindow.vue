<template>
  <div class="wrapper">
    <div class="window">
      <window-cross class="cross" @click="emit('close')"></window-cross>
      <div class="content">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
const emit = defineEmits(['close'])
</script>
<script lang="ts">
export default {
  name: "modal-window"
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
  position: relative;
}

.cross {
  position: absolute;  
  top: 27px;
  right: 27px;
}

.content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 40px;
}
</style>
