<script setup lang="ts"></script>

<template>
	<div class="fuji-header">
		<div class="logo"></div>
	</div>
</template>

<style scoped lang="scss">
.fuji-header {
	display: flex;
	flex-direction: row;
	justify-content: center;

	.logo {
		background-color: currentColor;
		color: $logo-color;
		width: 153px;
		height: 31px;
		fill: currentColor;

		mask: url("@/assets/icons/fuji_logo.svg") no-repeat;
		mask-size: cover;
	}
}
</style>
