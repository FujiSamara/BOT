<template>
	<span class="loader"></span>
</template>
<script lang="ts">
export default {
	name: "circle-loader",
};
</script>
<style scoped>
.loader {
	width: 48px;
	height: 48px;
	border-radius: 50%;
	display: flex;
	border-top: 3px solid #993ca6;
	border-right: 3px solid transparent;
	box-sizing: border-box;
	animation: rotation 1s linear infinite;
	position: absolute;
}

@keyframes rotation {
	0% {
		transform: rotate(0deg);
	}
	100% {
		transform: rotate(360deg);
	}
}
</style>
