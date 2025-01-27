<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

const emits = defineEmits(["close"]);

const keyDown = (e: KeyboardEvent) => {
	if (e.key === "Escape") {
		emits("close");
	}
};

onMounted(() => {
	document.addEventListener("keydown", keyDown);
});

onUnmounted(() => {
	document.removeEventListener("keydown", keyDown);
});
</script>

<template>
	<div class="bm-wrapper">
		<div class="bm-window">
			<slot></slot>
		</div>
	</div>
</template>

<style scoped lang="scss">
.bm-wrapper {
	left: 0;
	top: 0;
	position: fixed;

	z-index: 2;
	width: 100%;
	height: 100%;

	background: rgba(255, 255, 255, 0.1);
	backdrop-filter: blur(22px);
}
</style>
