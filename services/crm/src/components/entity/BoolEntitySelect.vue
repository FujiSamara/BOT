<script setup lang="ts">
import { PropType } from "vue";
import { BoolEntity } from "@/components/entity";
import Checkbox from "@/components/UI-new/Checkbox.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<BoolEntity>,
		required: true,
	},
});
const entity = props.entity;
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<Checkbox
			class="checkbox"
			:checked="entity.checked.value"
			@click="
				if (!entity.readonly) entity.checked.value = !entity.checked.value;
			"
		></Checkbox>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";

.checkbox {
	&.checked {
		background-color: $main-accent-blue;
	}
}
</style>
