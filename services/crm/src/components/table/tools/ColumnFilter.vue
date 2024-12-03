<script setup lang="ts"></script>

<template>
	<button class="cf-switch">
		<div class="tool-icon-wrapper">
			<div class="tool-icon filter"></div>
		</div>
		<span>Фильтр</span>
	</button>
</template>

<style scoped lang="scss">
.cf-switch {
	@include tool;

	.tool-icon-wrapper {
		.tool-icon {
			width: 15px;
			height: 10px;

			&.filter {
				mask-image: url("@/assets/icons/filter.svg");
			}
		}
	}
}
</style>
