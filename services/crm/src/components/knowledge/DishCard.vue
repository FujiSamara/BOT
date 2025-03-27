<script setup lang="ts">
import { PropType } from "vue";
import { DishCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
});
</script>
<template>
	<div class="dish-card"></div>
</template>
<style scoped lang="scss"></style>
