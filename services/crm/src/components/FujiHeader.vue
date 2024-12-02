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

		mask-image: url("@/assets/icons/logo.svg");
		mask-size: cover;
		mask-repeat: no-repeat;
	}

	&.short {
		.logo {
			width: 30.56px;
			height: 20.4px;
			mask-image: url("@/assets/icons/logo-short.svg");
		}
	}
}
</style>
