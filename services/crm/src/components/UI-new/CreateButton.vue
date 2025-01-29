<script setup lang="ts"></script>

<template>
	<button class="create-button">
		<div class="tool-icon-wrapper"><div class="tool-icon plus"></div></div>
	</button>
</template>

<style scoped lang="scss">
.create-button {
	width: 48px !important;
	height: 48px;
	@include field;
	justify-content: center;

	background-color: $main-accent-blue;
	border-color: $main-accent-blue;

	&:hover {
		background-color: $main-white;
		color: $bg-accent-blue-3;
	}

	.tool-icon-wrapper {
		.tool-icon {
			color: $main-white;
			width: 16.33px;
			height: 16.33px;

			&.plus {
				mask-image: url("@/assets/icons/plus.svg");
			}
		}
	}
}
</style>
